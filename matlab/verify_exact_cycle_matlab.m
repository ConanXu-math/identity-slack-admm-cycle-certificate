function result = verify_exact_cycle_matlab(outputPath, manifestPath)
    % VERIFY_EXACT_CYCLE_MATLAB Verify the frozen period-66 ADMM certificate.
    %   RESULT = VERIFY_EXACT_CYCLE_MATLAB() independently solves the exact
    %   six-dimensional period equation in the state (y,z,lambda), reruns the
    %   original ADMM iteration with the genuine componentwise positive-part
    %   projection, compares shared fields with instance_manifest.json, and
    %   writes certificate_matlab.json in the repository root.
    %
    %   RESULT = VERIFY_EXACT_CYCLE_MATLAB(OUTPUTPATH) writes the JSON result to
    %   OUTPUTPATH. Pass "" to skip writing a file.
    %
    %   RESULT = VERIFY_EXACT_CYCLE_MATLAB(OUTPUTPATH, MANIFESTPATH) compares
    %   against the specified Python-generated manifest.

    repoRoot = fileparts(fileparts(mfilename("fullpath")));
    if nargin < 1
        outputPath = fullfile(repoRoot, "certificate_matlab.json");
    end
    if nargin < 2
        manifestPath = fullfile(repoRoot, "instance_manifest.json");
    end
    outputPath = string(outputPath);
    manifestPath = string(manifestPath);

    assert(~isempty(ver("symbolic")), ...
           "ADMMCycle:MissingSymbolicMathToolbox", ...
           "Symbolic Math Toolbox is required for exact rational verification.");

    problem = buildProblem();
    [initialState, fixedDeterminant] = solvePeriodEquation(problem);
    period = size(problem.word, 1);
    states = sym(zeros(6, period + 1));
    states(:, 1) = initialState;
    margins = sym(zeros(2 * period, 1));

    sourceStrictChecks = false(period, 1);
    sourceWordChecks = false(period, 1);
    xOptimalityChecks = false(period, 1);
    yOptimalityChecks = false(period, 1);
    qDefinitionChecks = false(period, 1);
    projectionChecks = false(period, 1);
    complementarityChecks = false(period, 1);
    multiplierChecks = false(period, 1);

    for phase = 1:period
        state = states(:, phase);
        yState = state(1:2);
        zState = state(3:4);
        lambdaState = state(5:6);
        sourceQ = zState + lambdaState;
        [sourceMask, hasTie] = strictSignMask(sourceQ);
        expectedMask = problem.word(phase, :);

        sourceStrictChecks(phase) = ~hasTie;
        sourceWordChecks(phase) = ~hasTie && isequal(sourceMask, expectedMask);
        for coordinate = 1:2
            marginIndex = 2 * (phase - 1) + coordinate;
            if expectedMask(coordinate) == 1
                margins(marginIndex) = sourceQ(coordinate);
            else
                margins(marginIndex) = -sourceQ(coordinate);
            end
        end

        [xNext, qNext, nextState] = actualStep(state, problem);
        yNext = nextState(1:2);
        zNext = nextState(3:4);
        lambdaNext = nextState(5:6);
        residual = xNext + yNext + zNext - problem.rhs;

        xOptimalityChecks(phase) = isZeroMatrix( ...
                                                (problem.Q1 + problem.I) * xNext ...
                                                - (lambdaState - yState - zState + problem.rhs));
        yOptimalityChecks(phase) = isZeroMatrix( ...
                                                (problem.Q2 + problem.I) * yNext ...
                                                - (lambdaState - xNext - zState + problem.rhs));
        qDefinitionChecks(phase) = isZeroMatrix( ...
                                                qNext - (problem.rhs - xNext - yNext + lambdaState));
        projectionChecks(phase) = isZeroMatrix(zNext - positivePart(qNext));
        complementarityChecks(phase) = allExactNonnegative(zNext) ...
            && allExactNonpositive(lambdaNext) ...
            && isExactZero(zNext.' * lambdaNext);
        multiplierChecks(phase) = isZeroMatrix( ...
                                               lambdaNext - (lambdaState - residual));
        states(:, phase + 1) = nextState;
    end

    minimumMargin = exactMinimum(margins);
    minimumIndex = findExactValue(margins, minimumMargin);
    kktState = [problem.yStar; problem.zStar; problem.lambdaStar];

    q1PositiveDefinite = isZeroMatrix(problem.Q1 - problem.Q1.') ...
        && isExactPositive(problem.Q1(1, 1)) ...
        && isExactPositive(det(problem.Q1));
    q2PositiveDefinite = isZeroMatrix(problem.Q2 - problem.Q2.') ...
        && isExactPositive(problem.Q2(1, 1)) ...
        && isExactPositive(det(problem.Q2));

    checks = struct();
    checks.all_data_and_states_are_exact_rationals = isempty(symvar([ ...
                                                                     problem.Q1(:); problem.Q2(:); problem.rhs(:); states(:)]));
    checks.Q1_positive_definite = q1PositiveDefinite;
    checks.Q2_positive_definite = q2PositiveDefinite;
    checks.KKT_primal_feasibility = isZeroMatrix( ...
                                                 problem.xStar + problem.yStar + problem.zStar - problem.rhs);
    checks.KKT_x_stationarity = isZeroMatrix( ...
                                             problem.Q1 * problem.xStar - problem.lambdaStar);
    checks.KKT_y_stationarity = isZeroMatrix( ...
                                             problem.Q2 * problem.yStar - problem.lambdaStar);
    checks.KKT_z_nonnegative = allExactNonnegative(problem.zStar);
    checks.KKT_lambda_nonpositive = allExactNonpositive(problem.lambdaStar);
    checks.KKT_complementarity = isExactZero( ...
                                             problem.zStar.' * problem.lambdaStar);
    checks.unique_KKT_from_strong_convexity = q1PositiveDefinite ...
        && q2PositiveDefinite ...
        && checks.KKT_primal_feasibility ...
        && checks.KKT_x_stationarity ...
        && checks.KKT_y_stationarity ...
        && checks.KKT_z_nonnegative ...
        && checks.KKT_lambda_nonpositive ...
        && checks.KKT_complementarity;
    checks.raw_period_system_invertible = ~isExactZero(fixedDeterminant);
    checks.all_source_projection_signs_strict = all(sourceStrictChecks);
    checks.raw_projection_itinerary_matches_word = all(sourceWordChecks);
    checks.all_x_subproblem_equalities_exact = all(xOptimalityChecks);
    checks.all_y_subproblem_equalities_exact = all(yOptimalityChecks);
    checks.all_projection_arguments_exact = all(qDefinitionChecks);
    checks.all_positive_part_updates_exact = all(projectionChecks);
    checks.all_stepwise_complementarity_conditions = all(complementarityChecks);
    checks.all_multiplier_updates_exact = all(multiplierChecks);
    checks.all_132_branch_margins_positive = allExactPositive(margins);
    checks.uniform_margin_gt_1_over_1000 = isExactPositive( ...
                                                           minimumMargin - problem.marginThreshold);
    checks.exact_return_at_phase_66 = isZeroMatrix( ...
                                                   states(:, period + 1) - states(:, 1));
    checks.no_earlier_state_return = noEarlierReturn(states(:, 1:period));
    checks.mask_word_is_primitive = isPrimitiveWord(problem.word);
    checks.all_66_source_states_are_non_KKT = allStatesDiffer( ...
                                                              states(:, 1:period), kktState);

    initialY = initialState(1:2);
    initialQ = initialState(3:4) + initialState(5:6);
    agreement = compareManifest(manifestPath, problem, initialY, initialQ, ...
                                minimumMargin, minimumIndex);
    mathematicalValid = all(cell2mat(struct2cell(checks)));
    valid = mathematicalValid && agreement.all_shared_fields_match;

    result = struct();
    result.schema_version = 1;
    result.instance_id = problem.instanceId;
    result.implementation = "independent_matlab_symbolic_raw_6d";
    result.implementation_boundary = [ ...
                                      "MATLAB independently solves the affine period equation in " ...
                                      "(y,z,lambda) and accepts only after rerunning the genuine " ...
                                      "componentwise positive-part ADMM projection."];
    result.status = conditionalString(valid, "passed", "failed");
    result.valid = valid;
    result.mathematical_valid = mathematicalValid;
    result.formulation = "pure_quadratic_zero_linear_terms";
    result.parameters = struct( ...
                               'beta', "1", ...
                               'epsilon', exactString(problem.epsilon), ...
                               'mu', exactString(problem.mu), ...
                               'nu', exactString(problem.nu));
    result.period = period;
    result.word_run_length_encoding = {{"00", 2}, {"01", 64}};
    result.minimum_margin = struct( ...
                                   'exact', exactString(minimumMargin), ...
                                   'decimal', decimalString(minimumMargin, 20), ...
                                   'phase_zero_based', floor((minimumIndex - 1) / 2), ...
                                   'coordinate_zero_based', mod(minimumIndex - 1, 2), ...
                                   'threshold_exact', exactString(problem.marginThreshold));
    result.initial_state = struct( ...
                                  'y0_exact', exactStrings(initialY), ...
                                  'y0_decimal', decimalStrings(initialY, 18), ...
                                  'q0_exact', exactStrings(initialQ), ...
                                  'q0_decimal', decimalStrings(initialQ, 18), ...
                                  'z0_exact', exactStrings(initialState(3:4)), ...
                                  'lambda0_exact', exactStrings(initialState(5:6)));
    result.kkt_point = struct( ...
                              'x_exact', exactStrings(problem.xStar), ...
                              'y_exact', exactStrings(problem.yStar), ...
                              'z_exact', exactStrings(problem.zStar), ...
                              'lambda_exact', exactStrings(problem.lambdaStar));
    result.checks = checks;
    result.python_manifest_agreement = agreement;
    symbolicInfo = ver("symbolic");
    result.runtime = struct( ...
                            'matlab', version, ...
                            'release', version("-release"), ...
                            'symbolic_math_toolbox', symbolicInfo.Version);
    result.claim_boundary = [ ...
                             "This exact bounded non-KKT period-66 orbit refutes unconditional " ...
                             "global convergence; it does not claim unbounded iterates. " ...
                             "Cross-language agreement is an internal reproducibility check."];

    if strlength(outputPath) > 0
        writeJson(result, outputPath);
    end
end

function problem = buildProblem()
    epsilon = sym(1) / 1000;
    mu = sym(8957) / 10000;
    nu = sym(999) / 1000;
    identity = sym(eye(2));
    firstDirection = sym([-1; 20]);
    secondDirection = sym([-1; 10]);
    mMatrix = epsilon * identity + (mu - epsilon) ...
        * (firstDirection * firstDirection.') ...
        / (firstDirection.' * firstDirection);
    nMatrix = epsilon * identity + (nu - epsilon) ...
        * (secondDirection * secondDirection.') ...
        / (secondDirection.' * secondDirection);
    q1Matrix = inv(mMatrix) - identity;
    q2Matrix = inv(nMatrix) - identity;
    zStar = sym([0; 1]);
    lambdaStar = sym([-1; 0]);
    xStar = q1Matrix \ lambdaStar;
    yStar = q2Matrix \ lambdaStar;
    rhs = xStar + yStar + zStar;
    word = [zeros(2, 2); repmat([0, 1], 64, 1)];

    problem = struct();
    problem.instanceId = "identity_slack_p66_short_v1";
    problem.I = identity;
    problem.M = mMatrix;
    problem.N = nMatrix;
    problem.Q1 = q1Matrix;
    problem.Q2 = q2Matrix;
    problem.rhs = rhs;
    problem.xStar = xStar;
    problem.yStar = yStar;
    problem.zStar = zStar;
    problem.lambdaStar = lambdaStar;
    problem.word = word;
    problem.epsilon = epsilon;
    problem.mu = mu;
    problem.nu = nu;
    problem.marginThreshold = sym(1) / 1000;
end

function [xNext, yNext, qNext] = rawQuantities(state, problem)
    yState = state(1:2);
    zState = state(3:4);
    lambdaState = state(5:6);
    xNext = problem.M * (lambdaState - yState - zState + problem.rhs);
    yNext = problem.N * (lambdaState - xNext - zState + problem.rhs);
    qNext = problem.rhs - xNext - yNext + lambdaState;
end

function nextState = selectedStep(state, problem, selector)
    [~, yNext, qNext] = rawQuantities(state, problem);
    zNext = selector * qNext;
    lambdaNext = qNext - zNext;
    nextState = [yNext; zNext; lambdaNext];
end

function [xNext, qNext, nextState] = actualStep(state, problem)
    [xNext, yNext, qNext] = rawQuantities(state, problem);
    zNext = positivePart(qNext);
    lambdaNext = qNext - zNext;
    nextState = [yNext; zNext; lambdaNext];
end

function projected = positivePart(vector)
    projected = sym(zeros(size(vector)));
    for index = 1:numel(vector)
        if isExactPositive(vector(index))
            projected(index) = vector(index);
        elseif isExactNegative(vector(index))
            projected(index) = sym(0);
        else
            error("ADMMCycle:ProjectionTie", ...
                  "The exact projection argument contains a zero component.");
        end
    end
end

function [mask, hasTie] = strictSignMask(vector)
    mask = zeros(1, numel(vector));
    hasTie = false;
    for index = 1:numel(vector)
        if isExactPositive(vector(index))
            mask(index) = 1;
        elseif isExactNegative(vector(index))
            mask(index) = 0;
        else
            hasTie = true;
        end
    end
end

function lift = affineLift(problem, selector)
    origin = sym(zeros(6, 1));
    offset = selectedStep(origin, problem, selector);
    affine = sym(zeros(6, 7));
    affine(:, 7) = offset;
    for index = 1:6
        basis = sym(zeros(6, 1));
        basis(index) = 1;
        affine(:, index) = selectedStep(basis, problem, selector) - offset;
    end
    lift = [affine; sym([zeros(1, 6), 1])];
end

function [initialState, fixedDeterminant] = solvePeriodEquation(problem)
    lift00 = affineLift(problem, sym(diag([0, 0])));
    lift01 = affineLift(problem, sym(diag([0, 1])));
    period = size(problem.word, 1);
    periodLift = sym(eye(7));
    for sourcePhase = 1:period
        targetPhase = mod(sourcePhase, period) + 1;
        targetMask = problem.word(targetPhase, :);
        if isequal(targetMask, [0, 0])
            targetLift = lift00;
        elseif isequal(targetMask, [0, 1])
            targetLift = lift01;
        else
            error("ADMMCycle:UnexpectedMask", ...
                  "The frozen word contains an unsupported mask.");
        end
        periodLift = targetLift * periodLift;
    end
    fixedMatrix = sym(eye(6)) - periodLift(1:6, 1:6);
    fixedDeterminant = det(fixedMatrix);
    if isExactZero(fixedDeterminant)
        error("ADMMCycle:SingularPeriodSystem", ...
              "The exact six-dimensional period system is singular.");
    end
    initialState = fixedMatrix \ periodLift(1:6, 7);
end

function agreement = compareManifest(manifestPath, problem, initialY, ...
                                     initialQ, minimumMargin, minimumIndex)
    assert(isfile(manifestPath), "ADMMCycle:MissingManifest", ...
           "Python instance manifest not found: %s", manifestPath);
    manifest = jsondecode(fileread(manifestPath));
    shared = manifest.shared_certificate;
    wordEncoding = erase(jsonencode(shared.word_run_length_encoding), whitespacePattern);

    agreement = struct();
    agreement.instance_id_matches = string(shared.instance_id) == problem.instanceId;
    agreement.formulation_matches = string(shared.formulation) ...
        == "pure_quadratic_zero_linear_terms";
    agreement.parameters_match = string(shared.parameters.beta) == "1" ...
        && string(shared.parameters.epsilon) == exactString(problem.epsilon) ...
        && string(shared.parameters.mu) == exactString(problem.mu) ...
        && string(shared.parameters.nu) == exactString(problem.nu);
    agreement.period_matches = shared.period == size(problem.word, 1);
    agreement.mask_word_matches = strcmp(wordEncoding, '[["00",2],["01",64]]');
    agreement.minimum_margin_exact_matches = ...
        string(shared.minimum_margin.exact) == exactString(minimumMargin);
    agreement.minimum_margin_location_matches = ...
        shared.minimum_margin.phase_zero_based == floor((minimumIndex - 1) / 2) ...
        && shared.minimum_margin.coordinate_zero_based == mod(minimumIndex - 1, 2);
    agreement.margin_threshold_matches = ...
        string(shared.minimum_margin.threshold_exact) ...
        == exactString(problem.marginThreshold);
    agreement.y0_exact_matches = exactVectorMatches( ...
                                                    shared.initial_state.y0_exact, initialY);
    agreement.q0_exact_matches = exactVectorMatches( ...
                                                    shared.initial_state.q0_exact, initialQ);
    agreement.all_shared_fields_match = all(cell2mat(struct2cell(agreement)));
end

function matches = exactVectorMatches(jsonValues, symbolicValues)
    matches = isequal(string(jsonValues(:)), string(exactStrings(symbolicValues)));
end

function minimum = exactMinimum(values)
    minimum = values(1);
    for index = 2:numel(values)
        if isExactNegative(values(index) - minimum)
            minimum = values(index);
        end
    end
end

function index = findExactValue(values, target)
    index = 0;
    for candidate = 1:numel(values)
        if isExactZero(values(candidate) - target)
            index = candidate;
            break
        end
    end
    assert(index > 0, "ADMMCycle:MinimumNotFound", ...
           "The minimum margin could not be located.");
end

function passed = noEarlierReturn(states)
    passed = true;
    for phase = 2:size(states, 2)
        if isZeroMatrix(states(:, phase) - states(:, 1))
            passed = false;
            return
        end
    end
end

function passed = allStatesDiffer(states, reference)
    passed = true;
    for phase = 1:size(states, 2)
        if isZeroMatrix(states(:, phase) - reference)
            passed = false;
            return
        end
    end
end

function primitive = isPrimitiveWord(word)
    period = size(word, 1);
    primitive = true;
    for divisor = 1:(period - 1)
        if mod(period, divisor) == 0
            repeated = repmat(word(1:divisor, :), period / divisor, 1);
            if isequal(repeated, word)
                primitive = false;
                return
            end
        end
    end
end

function passed = allExactPositive(values)
    passed = true;
    for index = 1:numel(values)
        if ~isExactPositive(values(index))
            passed = false;
            return
        end
    end
end

function passed = allExactNonnegative(values)
    passed = true;
    for index = 1:numel(values)
        if ~(isExactPositive(values(index)) || isExactZero(values(index)))
            passed = false;
            return
        end
    end
end

function passed = allExactNonpositive(values)
    passed = true;
    for index = 1:numel(values)
        if ~(isExactNegative(values(index)) || isExactZero(values(index)))
            passed = false;
            return
        end
    end
end

function value = isExactPositive(expression)
    value = isAlways(expression > 0, "Unknown", "false");
end

function value = isExactNegative(expression)
    value = isAlways(expression < 0, "Unknown", "false");
end

function value = isExactZero(expression)
    value = isAlways(expression == 0, "Unknown", "false");
end

function value = isZeroMatrix(matrix)
    value = all(isAlways(matrix == 0, "Unknown", "false"), "all");
end

function text = exactString(value)
    text = string(char(value));
end

function texts = exactStrings(values)
    texts = strings(numel(values), 1);
    for index = 1:numel(values)
        texts(index) = exactString(values(index));
    end
end

function text = decimalString(value, digits)
    text = string(char(vpa(value, digits)));
end

function texts = decimalStrings(values, digits)
    texts = strings(numel(values), 1);
    for index = 1:numel(values)
        texts(index) = decimalString(values(index), digits);
    end
end

function value = conditionalString(condition, trueValue, falseValue)
    if condition
        value = trueValue;
    else
        value = falseValue;
    end
end

function writeJson(payload, outputPath)
    parent = fileparts(outputPath);
    if strlength(parent) > 0 && ~isfolder(parent)
        mkdir(parent);
    end
    fileIdentifier = fopen(outputPath, "w");
    assert(fileIdentifier >= 0, "ADMMCycle:CannotWriteCertificate", ...
           "Cannot open output path for writing: %s", outputPath);
    cleanup = onCleanup(@() fclose(fileIdentifier));
    fprintf(fileIdentifier, "%s\n", jsonencode(payload, "PrettyPrint", true));
    clear cleanup;
end

classdef VerifyExactCycleMatlabTest < matlab.unittest.TestCase
    % VERIFYEXACTCYCLEMATLABTEST Regression test for the frozen certificate.

    properties (SetAccess = private)
        Certificate
    end

    methods (TestClassSetup)

        function buildCertificate(testCase)
            testDirectory = fileparts(mfilename("fullpath"));
            repoRoot = fileparts(fileparts(testDirectory));
            testCase.applyFixture(matlab.unittest.fixtures.PathFixture( ...
                                                                       fullfile(repoRoot, "matlab")));
            testCase.Certificate = verify_exact_cycle_matlab("");
        end

    end

    methods (Test)

        function testFrozenExactCertificate(testCase)
            result = testCase.Certificate;

            testCase.verifyTrue(result.valid);
            testCase.verifyTrue(result.mathematical_valid);
            testCase.verifyEqual(result.instance_id, ...
                                 "identity_slack_p66_short_v1");
            testCase.verifyEqual(result.period, 66);
            testCase.verifyEqual(result.minimum_margin.threshold_exact, ...
                                 "1/1000");
            testCase.verifyTrue(result.checks.exact_return_at_phase_66);
            testCase.verifyTrue(result.checks.no_earlier_state_return);
            testCase.verifyTrue( ...
                                result.checks.all_132_branch_margins_positive);
            testCase.verifyTrue( ...
                                result.python_manifest_agreement.all_shared_fields_match);
        end

    end
end

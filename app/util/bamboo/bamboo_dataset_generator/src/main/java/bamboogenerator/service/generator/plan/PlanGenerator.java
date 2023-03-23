package bamboogenerator.service.generator.plan;

import bamboogenerator.model.PlanInfo;
import com.atlassian.bamboo.specs.api.builders.AtlassianModule;
import com.atlassian.bamboo.specs.api.builders.Variable;
import com.atlassian.bamboo.specs.api.builders.plan.Job;
import com.atlassian.bamboo.specs.api.builders.plan.Plan;
import com.atlassian.bamboo.specs.api.builders.plan.Stage;
import com.atlassian.bamboo.specs.api.builders.plan.artifact.Artifact;
import com.atlassian.bamboo.specs.api.builders.project.Project;
import com.atlassian.bamboo.specs.api.builders.task.AnyTask;
import com.atlassian.bamboo.specs.builders.repository.git.GitRepository;
import com.atlassian.bamboo.specs.builders.task.CheckoutItem;
import com.atlassian.bamboo.specs.builders.task.ScriptTask;
import com.atlassian.bamboo.specs.builders.task.TestParserTask;
import com.atlassian.bamboo.specs.builders.task.VcsCheckoutTask;
import com.atlassian.bamboo.specs.model.task.TestParserTaskProperties;
import com.atlassian.bamboo.specs.util.MapBuilder;

import java.util.List;
import java.util.stream.Collectors;

import static bamboogenerator.service.generator.plan.InlineBodies.BODY_FAIL;
import static bamboogenerator.service.generator.plan.InlineBodies.BODY_SUCCESS;

public class PlanGenerator {
    private static final int TEST_COUNT = 1000;
    private static final String RESULT_NAME_FAIL = "failed.xml";
    private static final String RESULT_NAME_SUCCESS = "success.xml";

    public static List<Plan> generate(List<PlanInfo> planInfoList) {
        return planInfoList.stream()
                .map(PlanGenerator::createPlan)
                .collect(Collectors.toList());
    }

    private static Plan createPlan(PlanInfo planInfo) {
        boolean isFailedPlan = planInfo.isFailed();
        return new Plan(new Project().name(planInfo.getProjectName())
                .key(planInfo.getProjectKey()), planInfo.getPlanName(), planInfo.getPlanKey())
                .description("DCAPT Bamboo test build plan")
                .planRepositories(new GitRepository()
                        .name("dcapt-test-repo")
                        .url("https://bitbucket.org/atlassianlabs/dcapt-bamboo-test-repo.git")
                        .branch("master"))
                .variables(new Variable("stack_name", ""))
                .stages(new Stage("Stage 1")
                        .jobs(new Job("Job 1", "JB1")
                                .tasks(
                                        new VcsCheckoutTask()
                                                .description("Checkout repository task")
                                                .cleanCheckout(true)
                                                .checkoutItems(new CheckoutItem()
                                                        .repository("dcapt-test-repo").path("dcapt-test-repo")),
                                        new ScriptTask()
                                                .description("Run Bash code")
                                                .interpreterBinSh()
                                                .inlineBody("for i in $(seq 1 1000); do date=$(date -u); echo $date >> results.log; echo $date; sleep 0.06; done"),
                                        new ScriptTask()
                                                .description("Write XML test results")
                                                .interpreterBinSh()
                                                .inlineBody(isFailedPlan
                                                        ? String.format(BODY_FAIL, TEST_COUNT, TEST_COUNT, TEST_COUNT)
                                                        : String.format(BODY_SUCCESS, TEST_COUNT, TEST_COUNT)),
                                        new AnyTask(new AtlassianModule("net.utoolity.atlassian.bamboo.tasks-for-aws:aws.cloudformation.stack"))
                                                .description("Validate CFN template")
                                                .configuration(new MapBuilder()
                                                        .put("changeSetDescription", "")
                                                        .put("stackPolicyURL", "")
                                                        .put("stackPolicyDuringUpdateURL", "")
                                                        .put("ignoreNoOpUpdateExceptionUpdate", "true")
                                                        .put("awsIamRoleAgentsArn", "")
                                                        .put("ignoreNoopCreateChangeSetFailure", "")
                                                        .put("stackName", "")
                                                        .put("pluginVersionOnSave", "2.21.3")
                                                        .put("enableIAM", "")
                                                        .put("ignoreNoOpUpdateExceptionCreate", "true")
                                                        .put("changeSetName", "")
                                                        .put("variableNamespace", "custom.aws")
                                                        .put("resourceAction", "Validate")
                                                        .put("pluginConfigVersionOnSave", "11")
                                                        .put("templateParameters", "")
                                                        .put("roleArn", "")
                                                        .put("resourceRegionVariable", "")
                                                        .put("stackPolicyBody", "")
                                                        .put("changeSetType", "CREATE_OR_UPDATE")
                                                        .put("doNotFailIfNotExists", "")
                                                        .put("templateParametersJson", "")
                                                        .put("createIfNotExists", "")
                                                        .put("stackNameOrId", "")
                                                        .put("stackPolicyDuringUpdateBody", "")
                                                        .put("changeSetNameOrArn", "")
                                                        .put("capabilities", "[]")
                                                        .put("secretKey", "BAMSCRT@0@0@W3vUSvo2EtgGKbZfg+ORYA==")
                                                        .put("templateSource", "BODY")
                                                        .put("onFailureOption", "ROLLBACK")
                                                        .put("resourceRegion", "us-east-1")
                                                        .put("templateURL", "")
                                                        .put("snsTopic", "")
                                                        .put("stackNameOrIdWithChangeSetName", "")
                                                        .put("accessKey", "")
                                                        .put("creationTimeout", "")
                                                        .put("templateBody", "AWSTemplateFormatVersion: '2010-09-09'\nDescription: |\n  AWS CloudFormation Sample Template Parameter_Validate: Sample template\n  showing how to validate and type parameters. This template does not create any billable\n  AWS Resources.\nParameters:\n  NumberWithRange:\n    Type: Number\n    MinValue: '1'\n    MaxValue: '10'\n    Default: '2'\n    Description: Enter a number between 1 and 10, default is 2\n  NumberWithAllowedValues:\n    Type: Number\n    Default: '2'\n    AllowedValues:\n    - '1'\n    - '2'\n    - '3'\n    - '10'\n    - '20'\n    Description: Enter 1,2,3,10 or 20, default is 2\n  StringWithLength:\n    Type: String\n    Default: Hello World\n    MaxLength: '20'\n    MinLength: '5'\n    Description: Enter a string, between 5 and 20 characters in length\n    ConstraintDescription: must have between 5 and 20 characters\n  StringWithAllowedValues:\n    Type: String\n    Default: t2.small\n    AllowedValues:\n    - t1.micro\n    - t2.nano\n    - t2.micro\n    - t2.small\n    - t2.medium\n    - t2.large\n    - m1.small\n    - m1.medium\n    - m1.large\n    - m1.xlarge\n    - m2.xlarge\n    - m2.2xlarge\n    - m2.4xlarge\n    - m3.medium\n    - m3.large\n    - m3.xlarge\n    - m3.2xlarge\n    - m4.large\n    - m4.xlarge\n    - m4.2xlarge\n    - m4.4xlarge\n    - m4.10xlarge\n    - c1.medium\n    - c1.xlarge\n    - c3.large\n    - c3.xlarge\n    - c3.2xlarge\n    - c3.4xlarge\n    - c3.8xlarge\n    - c4.large\n    - c4.xlarge\n    - c4.2xlarge\n    - c4.4xlarge\n    - c4.8xlarge\n    - g2.2xlarge\n    - g2.8xlarge\n    - r3.large\n    - r3.xlarge\n    - r3.2xlarge\n    - r3.4xlarge\n    - r3.8xlarge\n    - i2.xlarge\n    - i2.2xlarge\n    - i2.4xlarge\n    - i2.8xlarge\n    - d2.xlarge\n    - d2.2xlarge\n    - d2.4xlarge\n    - d2.8xlarge\n    - hi1.4xlarge\n    - hs1.8xlarge\n    - cr1.8xlarge\n    - cc2.8xlarge\n    - cg1.4xlarge\n    Description: Enter a valid EC2 instance type. Default is t2.small\n    ConstraintDescription: must be a valid EC2 instance type\n  StringWithRegex:\n    Type: String\n    Default: Hello\n    AllowedPattern: '[A-Za-z0-9]+'\n    MaxLength: '10'\n    Description: Enter a string with alpha-numeric characters only\n    ConstraintDescription: must only contain upper and lower case letters and numbers\n  # KeyName:\n  #   Description: EC2 Key Pair\n  #   Type: AWS::EC2::KeyPair::KeyName\n  #   ConstraintDescription: must be the name of an existing EC2 KeyPair.\n  # NOTE: TypedList example deliberately omitted to work around HTML parsing issues with brackets\nResources:\n  DummyResource:\n    Type: AWS::CloudFormation::WaitConditionHandle\nOutputs:\n  NumberWithRange:\n    Value: !Ref 'NumberWithRange'\n  NumberWithAllowedValues:\n    Value: !Ref 'NumberWithAllowedValues'\n  StringWithLength:\n    Value: !Ref 'StringWithLength'\n  StringWithAllowedValue:\n    Value: !Ref 'StringWithAllowedValues'\n  StringWithRegex:\n    Value: !Ref 'StringWithRegex'\n  # KeyName:\n  #   Value: !Ref 'KeyName'")
                                                        .put("sessionToken", "")
                                                        .put("stackPolicyDuringUpdateSource", "URL")
                                                        .put("awsCredentialsSource", "IFAWS_CONNECTOR")
                                                        .put("awsConnectorIdVariable", "${bamboo.awsDefaultConnector}")
                                                        .put("stackTags", "")
                                                        .put("stackPolicySource", "URL")
                                                        .put("awsConnectorId", "AWS_CONNECTOR_VARIABLE_KEY")
                                                        .put("updateIfExists", "")
                                                        .put("variableScope", "LOCAL")
                                                        .build()
                                                )
                                )
                                .finalTasks(new TestParserTask(TestParserTaskProperties.TestType.JUNIT)
                                        .description("Unit test results parser task")
                                        .resultDirectories(isFailedPlan ? RESULT_NAME_FAIL : RESULT_NAME_SUCCESS)
                                )
                                .artifacts(new Artifact("Test Reports")
                                        .location(".")
                                        .copyPattern("*.log"))));
    }
}

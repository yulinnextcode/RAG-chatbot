<#
.SYNOPSIS
  Deploy network -> efs -> compute CloudFormation stacks for RAG-CHATBOT.

USAGE (PowerShell):
  PS> & ".\deploy.ps1" -Env dev -KeyName my-key -AdminCidr "203.0.113.4/32" -Profile default -Region us-east-1 -EnableCloudWatch $true

Note:
 - Do NOT dot-source the script (do not run ". .\deploy.ps1 ..."). Use .\deploy.ps1 or & '.\deploy.ps1'.
#>

param(
  [Parameter(Mandatory=$true)][string]$Env,
  [Parameter(Mandatory=$true)][string]$KeyName,
  [Parameter(Mandatory=$true)][string]$AdminCidr,
  [Parameter(Mandatory=$false)][string]$Profile = "default",
  [Parameter(Mandatory=$false)][string]$Region = "us-east-1",
  [Parameter(Mandatory=$false)][bool]$EnableCloudWatch = $true
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Resolve aws cli executable path
try {
    $awsCmd = Get-Command aws -ErrorAction Stop
    $awsExePath = $awsCmd.Source
} catch {
    Write-Error "Unable to find 'aws' in PATH. Install AWS CLI v2 and ensure 'aws' is on PATH."
    throw
}

function Run-Aws {
    param(
        [Parameter(Mandatory=$true, ValueFromRemainingArguments=$true)]
        [string[]]$Args
    )

    # Final argument array includes profile and region
    $cmdArgs = @($Args) + @("--profile", $Profile, "--region", $Region)

    # Create temp files for stdout/stderr
    $outFile = [System.IO.Path]::GetTempFileName()
    $errFile = [System.IO.Path]::GetTempFileName()

    try {
        Write-Host "Running: `"$awsExePath $($cmdArgs -join ' ')`""

        $startInfo = @{
            FilePath = $awsExePath
            ArgumentList = $cmdArgs
            NoNewWindow = $true
            Wait = $true
            PassThru = $true
            RedirectStandardOutput = $outFile
            RedirectStandardError  = $errFile
        }

        $proc = Start-Process @startInfo

        # Read outputs (use -Raw to preserve formatting)
        $stdOut = if (Test-Path $outFile) { Get-Content -Raw -Path $outFile } else { "" }
        $stdErr = if (Test-Path $errFile) { Get-Content -Raw -Path $errFile } else { "" }

        if ($stdOut) { Write-Host $stdOut }
        if ($stdErr) { Write-Host $stdErr }

        $exitCode = $proc.ExitCode

        if ($exitCode -ne 0) {
            throw "aws command failed (exit code $exitCode). See output above for details."
        }

        return $stdOut
    } finally {
        # Cleanup temp files
        if (Test-Path $outFile) { Remove-Item $outFile -ErrorAction SilentlyContinue }
        if (Test-Path $errFile) { Remove-Item $errFile -ErrorAction SilentlyContinue }
    }
}

# Stack names and templates
$stackPrefix = "${Env}-chatbot"
$networkStack = "${stackPrefix}-network"
$efsStack     = "${stackPrefix}-efs"
$computeStack = "${stackPrefix}-compute"

$scriptDir = Split-Path -Parent $PSCommandPath
$templateRoot = Join-Path $scriptDir ".."

# Resolve template paths (will throw if file doesn't exist)
$networkTemplate = (Resolve-Path (Join-Path $templateRoot "network\network-stack.yaml")).Path
$efsTemplate     = (Resolve-Path (Join-Path $templateRoot "efs\efs-stack.yaml")).Path
$computeTemplate = (Resolve-Path (Join-Path $templateRoot "compute\compute-stack.yaml")).Path

Write-Host "Using AWS profile: $Profile  region: $Region"
Write-Host "Network template: $networkTemplate"
Write-Host "EFS template: $efsTemplate"
Write-Host "Compute template: $computeTemplate"

# Validate templates (using file:// paths wrapped in quotes to handle spaces)
Write-Host "`nValidating network template..."
Run-Aws cloudformation validate-template --template-body "file://$networkTemplate"

Write-Host "`nValidating EFS template..."
Run-Aws cloudformation validate-template --template-body "file://$efsTemplate"

Write-Host "`nValidating compute template..."
Run-Aws cloudformation validate-template --template-body "file://$computeTemplate"

# Deploy stacks
Write-Host "`nDeploying network stack: $networkStack"
Run-Aws cloudformation deploy --stack-name $networkStack --template-file "$networkTemplate" --capabilities CAPABILITY_NAMED_IAM --parameter-overrides "EnvName=$Env" "AdminCidr=$AdminCidr" "EnableNat=true"
Run-Aws cloudformation wait stack-create-complete --stack-name $networkStack

Write-Host "`nDeploying EFS stack: $efsStack"
Run-Aws cloudformation deploy --stack-name $efsStack --template-file "$efsTemplate" --capabilities CAPABILITY_NAMED_IAM --parameter-overrides "EnvName=$Env" "EfsKmsKeyId="
Run-Aws cloudformation wait stack-create-complete --stack-name $efsStack

$enableCwString = if ($EnableCloudWatch) { "true" } else { "false" }
Write-Host "`nDeploying compute stack: $computeStack (EnableCloudWatch=$enableCwString)"
Run-Aws cloudformation deploy --stack-name $computeStack --template-file "$computeTemplate" --capabilities CAPABILITY_NAMED_IAM --parameter-overrides "EnvName=$Env" "KeyName=$KeyName" "EnableCloudWatch=$enableCwString"
Run-Aws cloudformation wait stack-create-complete --stack-name $computeStack

Write-Host "`nCompute stack outputs:"
Run-Aws cloudformation describe-stacks --stack-name $computeStack --query "Stacks[0].Outputs" --output table

Write-Host "`nAll stacks deployed."
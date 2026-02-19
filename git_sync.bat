@echo off
:: %~1 is the path passed from Python
SET TARGET_DIR=%~1
SET BRANCH=main

IF "%TARGET_DIR%"=="" (
    echo Error: No target directory provided.
    exit /b 1
)

:: Change to the data directory (/d ensures it can switch drive letters if needed)
cd /d "%TARGET_DIR%" || exit /b 1

echo Syncing inside: %CD%

:: Add changes
git add .

:: Check for changes. If errorlevel is 0, there are no changes.
git diff --cached --quiet
IF %ERRORLEVEL% EQU 0 (
    echo No changes to commit.
    goto :PushPhase
)

:: Commit with timestamp
:: %DATE% and %TIME% are built-in Windows variables
SET TIMESTAMP=%DATE% %TIME%
git commit -m "Auto-Update: %TIMESTAMP%"

:PushPhase
:: 4. Push to remote
echo Pushing...
git push origin %BRANCH%
echo Pushed to Git
# build.ps1 — OptionAlpha Agent Master Build Script (Windows PowerShell)
# Builds all native components: Rust extension, C++ engine, Java monitoring server.
# Run from the project root: .\build.ps1

param(
    [switch]$RustOnly,
    [switch]$JavaOnly,
    [switch]$SkipJava,
    [switch]$Release
)

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot

function Write-Step($n, $msg) {
    Write-Host "`n$("="*55)" -ForegroundColor Cyan
    Write-Host "  Step $n — $msg" -ForegroundColor Cyan
    Write-Host "$("="*55)" -ForegroundColor Cyan
}
function Write-OK($msg)   { Write-Host "  OK  $msg" -ForegroundColor Green }
function Write-WARN($msg) { Write-Host "  WARN $msg" -ForegroundColor Yellow }
function Write-FAIL($msg) { Write-Host "  FAIL $msg" -ForegroundColor Red }

# ── Step 1: Python venv check ─────────────────────────────────
Write-Step 1 "Python Virtual Environment"
$venv = Join-Path $Root ".venv\Scripts\python.exe"
if (!(Test-Path $venv)) {
    Write-Host "  Creating venv..." -ForegroundColor Gray
    python -m venv "$Root\.venv"
    & "$Root\.venv\Scripts\pip" install -r "$Root\requirements.txt" -q
    Write-OK "venv created and requirements installed"
} else {
    Write-OK "venv already exists"
}

if ($JavaOnly) { goto java_step }

# ── Step 2: Rust extension ────────────────────────────────────
Write-Step 2 "Rust Extension (optionalpha_data)"
$rustDir = Join-Path $Root "engine\rust"
if (Get-Command "cargo" -ErrorAction SilentlyContinue) {
    Push-Location $rustDir
    try {
        if ($Release) {
            & "$Root\.venv\Scripts\python" -m maturin build --release -q
            Write-OK "Rust release build complete"
        } else {
            & "$Root\.venv\Scripts\python" -m maturin develop -q
            Write-OK "Rust dev build complete (optionalpha_data importable)"
        }
    } catch {
        Write-WARN "Rust build failed — agent will use Python fallbacks"
        Write-WARN $_.Exception.Message
    } finally {
        Pop-Location
    }
} else {
    Write-WARN "cargo not found. Install Rust from https://rustup.rs/"
    Write-WARN "IV Rank & FeatureMatrix will use Python fallbacks"
}

if ($RustOnly) { exit 0 }

# ── Step 3: C++ engine (optional, ctypes) ────────────────────
Write-Step 3 "C++ Trading Engine (optional)"
$cppDir = Join-Path $Root "engine\cpp"
if (Get-Command "cmake" -ErrorAction SilentlyContinue) {
    Push-Location $cppDir
    try {
        New-Item -ItemType Directory -Force -Path "build" | Out-Null
        cmake -S . -B build -G "Ninja" -DCMAKE_BUILD_TYPE=Release -q
        cmake --build build --config Release -q
        Write-OK "C++ engine built → engine/cpp/build/"
    } catch {
        Write-WARN "C++ build failed — risk gate uses Python fallback"
    } finally {
        Pop-Location
    }
} else {
    Write-WARN "cmake not found. C++ engine unavailable (Python fallback active)"
}

# ── Step 4: Java monitoring server ───────────────────────────
:java_step
if (!$SkipJava) {
    Write-Step 4 "Java Monitoring Server"
    $javaDir = Join-Path $Root "engine\java"
    if (Get-Command "mvn" -ErrorAction SilentlyContinue) {
        Push-Location $javaDir
        try {
            mvn package -q -DskipTests
            Write-OK "Java server built → engine/java/target/optionalpha-monitor-1.0.jar"
            Write-OK "Start with: java -jar engine\java\target\optionalpha-monitor-1.0.jar --port=8181"
        } catch {
            Write-WARN "Maven build failed"
            Write-WARN $_.Exception.Message
        } finally {
            Pop-Location
        }
    } elseif (Get-Command "java" -ErrorAction SilentlyContinue) {
        Write-WARN "Java found but Maven (mvn) not found. Skipping server build."
        Write-WARN "Install Maven from https://maven.apache.org/"
    } else {
        Write-WARN "Java not found — monitoring server unavailable"
        Write-WARN "Install JDK 17+ from https://adoptium.net/"
    }
}

# ── Step 5: Julia packages ────────────────────────────────────
Write-Step 5 "Julia Packages (Options Math)"
if (Get-Command "julia" -ErrorAction SilentlyContinue) {
    julia -e "import Pkg; Pkg.add([\"PythonCall\",\"Distributions\",\"SpecialFunctions\"])" 2>&1 | Out-Null
    Write-OK "Julia packages installed (PythonCall, Distributions, SpecialFunctions)"
} else {
    Write-WARN "Julia not found. Options math will use Python/scipy fallback."
    Write-WARN "Download Julia from https://julialang.org/downloads/"
}

# ── Summary ───────────────────────────────────────────────────
Write-Host "`n$("="*55)" -ForegroundColor Green
Write-Host "  Build Complete" -ForegroundColor Green
Write-Host "$("="*55)`n" -ForegroundColor Green
Write-Host "  Next steps:" -ForegroundColor White
Write-Host "    1. Edit .env with Alpaca paper API keys"
Write-Host "    2. Train AI models:  .venv\Scripts\python run_agent.py --train-only"
Write-Host "    3. Run agent:        .venv\Scripts\python run_agent.py"
Write-Host "    4. Dashboard:        http://127.0.0.1:8080"
Write-Host ""

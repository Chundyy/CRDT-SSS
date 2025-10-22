# NetGuardian - Script de Criacao de ZIP para Distribuicao
# Cria um arquivo ZIP pronto para upload no GitHub ou distribuicao

$ErrorActionPreference = "Stop"

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  NetGuardian - Criar ZIP de Distribuicao" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Nome do arquivo ZIP
$zipName = "NetGuardian-v1.0.0.zip"

# Verificar se ja existe
if (Test-Path $zipName) {
    Write-Host "O ficheiro $zipName ja existe." -ForegroundColor Yellow
    $response = Read-Host "Sobrescrever? (S/N)"
    if ($response -ne "S" -and $response -ne "s") {
        Write-Host "Operacao cancelada." -ForegroundColor Red
        exit
    }
    Remove-Item $zipName -Force
}

# Ficheiros e pastas a EXCLUIR (sensiveis ou temporarios)
$excludePatterns = @(
    "\.env$",
    "encryption\.key$",
    "\.db$",
    "\.sqlite",
    "\.sqlite3$",
    "__pycache__",
    "\.pyc$",
    "\.pyo$",
    "venv",
    "\.venv",
    "env",
    "ENV",
    "local_files",
    "\.log$",
    "\.git",
    "\.vscode\\settings\.json",
    "\.idea",
    "\.DS_Store",
    "Thumbs\.db",
    "desktop\.ini",
    "\.zip$",
    "\.tmp$",
    "\.bak$",
    "user_\d+"
)

Write-Host "A recolher ficheiros..." -ForegroundColor Green

# Obter todos os ficheiros
$allFiles = Get-ChildItem -Recurse -File | Where-Object {
    $relativePath = $_.FullName.Substring($PWD.Path.Length + 1)
    
    # Verificar se o ficheiro NAO corresponde a nenhum padrao de exclusao
    $shouldExclude = $false
    foreach ($pattern in $excludePatterns) {
        if ($relativePath -match $pattern) {
            $shouldExclude = $true
            break
        }
    }
    
    -not $shouldExclude
}

Write-Host "Encontrados $($allFiles.Count) ficheiros para incluir" -ForegroundColor Green
Write-Host ""

# Listar ficheiros principais
Write-Host "Ficheiros principais incluidos:" -ForegroundColor Cyan
$mainFiles = @(
    "main.py",
    "setup.py",
    "requirements.txt",
    "README.md",
    "INSTALL.md",
    "CONTRIBUTING.md",
    "QUICKSTART.md",
    "LICENSE",
    ".gitignore",
    ".env.example"
)

foreach ($file in $mainFiles) {
    if (Test-Path $file) {
        Write-Host "  OK $file" -ForegroundColor Green
    } else {
        Write-Host "  AVISO $file (nao encontrado)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Modulos incluidos:" -ForegroundColor Cyan
$modules = @("src\auth", "src\crdt", "src\database", "src\file_manager", "src\gui", "src\utils", "config")
foreach ($module in $modules) {
    if (Test-Path $module) {
        $fileCount = (Get-ChildItem "$module\*.py" -Recurse -File | Measure-Object).Count
        Write-Host "  OK $module ($fileCount ficheiros .py)" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "A criar arquivo ZIP..." -ForegroundColor Green

# Criar ZIP
try {
    Compress-Archive -Path $allFiles.FullName -DestinationPath $zipName -CompressionLevel Optimal -Force
    
    $zipSize = [math]::Round((Get-Item $zipName).Length / 1MB, 2)
    
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Green
    Write-Host "  ZIP criado com sucesso!" -ForegroundColor Green
    Write-Host "================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Ficheiro: $zipName" -ForegroundColor Cyan
    Write-Host "Tamanho: $zipSize MB" -ForegroundColor Cyan
    Write-Host "Ficheiros: $($allFiles.Count)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Proximos passos:" -ForegroundColor Yellow
    Write-Host "  1. Fazer upload para GitHub Releases" -ForegroundColor White
    Write-Host "  2. Ou partilhar directamente com outros utilizadores" -ForegroundColor White
    Write-Host ""
    Write-Host "IMPORTANTE:" -ForegroundColor Red
    Write-Host "  - Ficheiros sensiveis (.env, encryption.key) foram EXCLUIDOS" -ForegroundColor Yellow
    Write-Host "  - Utilizadores devem executar 'python setup.py' apos extrair" -ForegroundColor Yellow
    Write-Host ""
    
}
catch {
    Write-Host ""
    Write-Host "Erro ao criar ZIP: $_" -ForegroundColor Red
    exit 1
}

# Abrir pasta
$response = Read-Host "Abrir pasta no Explorer? (S/N)"
if ($response -eq "S" -or $response -eq "s") {
    explorer.exe /select,"$PWD\$zipName"
}

Write-Host ""
Write-Host "Concluido!" -ForegroundColor Green

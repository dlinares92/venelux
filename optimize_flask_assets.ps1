# Venelux Flask Asset Optimization Script
# Compresses MP4 videos, JPEGs, PNGs, and HEICs in the python/app/static/img directory.
# Requirements: ffmpeg must be installed and in your PATH.

$TargetDir = ".\python\app\static\img"
$ffmpeg = Get-Command ffmpeg -ErrorAction SilentlyContinue

if (-not $ffmpeg) {
    Write-Host "Error: ffmpeg no esta instalado. Por favor, instalalo desde https://ffmpeg.org/download.html" -ForegroundColor Red
    exit
}

Write-Host "--- Iniciando OPTIMIZACION PROFUNDA en $TargetDir ---" -ForegroundColor Cyan

# Extensiones a procesar
$VideoExts = @("*.mp4")
$ImageExts = @("*.jpg", "*.jpeg")

# 1. Procesar Videos
Write-Host ""
Write-Host "[1/2] Optimizando Videos (Max 720p)..." -ForegroundColor Yellow
$videos = Get-ChildItem -Path $TargetDir -Include $VideoExts -Recurse
foreach ($video in $videos) {
    $tempFile = "$($video.FullName).tmp.mp4"
    Write-Host "Procesando: $($video.Name)... " -NoNewline
    
    # -vf "scale='min(1280,iw)':-1" reduce a 720p si es muy grande
    # -crf 32 es agresivo pero ideal para reducir sustancialmente el peso en megabytes
    & ffmpeg -i "$($video.FullName)" -vcodec libx264 -crf 32 -preset fast -vf "scale='min(1280,iw)':-1" -movflags +faststart "$tempFile" -y -loglevel error
    
    if (Test-Path $tempFile) {
        $oldSize = (Get-Item $video.FullName).Length
        $newSize = (Get-Item $tempFile).Length
        
        if ($newSize -lt $oldSize) {
            $reduction = [math]::Round((($oldSize - $newSize) / $oldSize) * 100, 2)
            $oldMB = [math]::Round($oldSize/1MB, 2)
            $newMB = [math]::Round($newSize/1MB, 2)
            Move-Item -Path $tempFile -Destination $video.FullName -Force
            Write-Host "OK! Reduccion: $reduction% ($oldMB MB -> $newMB MB)" -ForegroundColor Green
        } else {
            Remove-Item $tempFile
            Write-Host "Saltado (ya estaba optimizado)" -ForegroundColor Gray
        }
    } else {
        Write-Host "Error al optimizar" -ForegroundColor Red
    }
}

# 2. Procesar Imagenes
Write-Host ""
Write-Host "[2/2] Optimizando Imagenes (Max 1600px)..." -ForegroundColor Yellow
$images = Get-ChildItem -Path $TargetDir -Include $ImageExts -Recurse
foreach ($img in $images) {
    $tempFile = "$($img.FullName).tmp.jpg"
    Write-Host "Optimizando: $($img.Name)... " -NoNewline
    
    # -vf "scale='min(1600,iw)':-1" escala a un maximo de 1600px de ancho
    # -q:v 70 es un nivel de compresion alto y ligero para web
    & ffmpeg -i "$($img.FullName)" -vf "scale='min(1600,iw)':-1" -q:v 70 "$tempFile" -y -loglevel error
    
    if (Test-Path $tempFile) {
        $oldSize = (Get-Item $img.FullName).Length
        $newSize = (Get-Item $tempFile).Length
        
        if ($newSize -lt $oldSize) {
            $reduction = [math]::Round((($oldSize - $newSize) / $oldSize) * 100, 2)
            $oldMB = [math]::Round($oldSize/1MB, 2)
            $newMB = [math]::Round($newSize/1MB, 2)
            Move-Item -Path $tempFile -Destination $img.FullName -Force
            Write-Host "OK! Reduccion: $reduction% ($oldMB MB -> $newMB MB)" -ForegroundColor Green
        } else {
            Remove-Item $tempFile
            Write-Host "Saltado" -ForegroundColor Gray
        }
    } else {
        Write-Host "Error al optimizar" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "--- Optimizacion Completada ---" -ForegroundColor Cyan
Write-Host "Las imagenes gigantes y videos ahora tienen el tamano correcto para la web."

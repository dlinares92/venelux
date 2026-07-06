# Venelux Asset Optimization Script - PHASE 2 (Deep Optimization)
# Compresses MP4 videos, JPEGs, PNGs, and HEICs in the public/img directory.
# Requirements: ffmpeg must be installed and in your PATH.

$TargetDir = ".\public\img"
$ffmpeg = Get-Command ffmpeg -ErrorAction SilentlyContinue

if (-not $ffmpeg) {
    Write-Host "Error: ffmpeg no est instalado. Por favor, instlalo desde https://ffmpeg.org/download.html" -ForegroundColor Red
    exit
}

Write-Host "--- Iniciando OPTIMIZACIN PROFUNDA en $TargetDir ---" -ForegroundColor Cyan

# Extensiones a procesar
$VideoExts = @("*.mp4")
$ImageExts = @("*.jpg", "*.jpeg", "*.png", "*.heic")

# 1. Procesar Videos
Write-Host "`n[1/2] Optimizando Videos (Max 720p)..." -ForegroundColor Yellow
$videos = Get-ChildItem -Path $TargetDir -Include $VideoExts -Recurse
foreach ($video in $videos) {
    $tempFile = "$($video.FullName).tmp.mp4"
    Write-Host "Procesando: $($video.Name)..." -NoNewline
    
    # -vf "scale='min(1280,iw)':-1" reduce a 720p si es muy grande
    # -crf 30 es ms agresivo para ahorrar espacio sin sacrificar demasiado la vista web
    & ffmpeg -i "$($video.FullName)" -vcodec libx264 -crf 30 -preset fast -vf "scale='min(1280,iw)':-1" -movflags +faststart "$tempFile" -y -loglevel error
    
    if (Test-Path $tempFile) {
        $oldSize = (Get-Item $video.FullName).Length
        $newSize = (Get-Item $tempFile).Length
        
        if ($newSize -lt $oldSize) {
            $reduction = [math]::Round((($oldSize - $newSize) / $oldSize) * 100, 2)
            Move-Item -Path $tempFile -Destination $video.FullName -Force
            Write-Host " OK! Reduccin del $reduction%" -ForegroundColor Green
        } else {
            Remove-Item $tempFile
            Write-Host " Saltado (ya estaba optimizado)" -ForegroundColor Gray
        }
    }
}

# 2. Procesar Imgenes
Write-Host "`n[2/2] Optimizando Imgenes (Max 1600px)..." -ForegroundColor Yellow
$images = Get-ChildItem -Path $TargetDir -Include $ImageExts -Recurse
foreach ($img in $images) {
    $ext = [io.path]::GetExtension($img.Name).ToLower()
    $destFile = $img.FullName
    
    # Si es HEIC, convertir a JPG para compatibilidad web
    if ($ext -eq ".heic") {
        $destFile = [io.path]::ChangeExtension($img.FullName, ".jpg")
    }
    
    $tempFile = "$($img.FullName).tmp.jpg"
    Write-Host "Optimizando: $($img.Name)..." -NoNewline
    
    # -vf "scale='min(1600,iw)':-1" escala a un mximo de 1600px de ancho
    # -q:v 75 es un nivel de calidad alto pero muy ligero (similar a Photoshop 60-70)
    & ffmpeg -i "$($img.FullName)" -vf "scale='min(1600,iw)':-1" -q:v 75 "$tempFile" -y -loglevel error
    
    if (Test-Path $tempFile) {
        $oldSize = (Get-Item $img.FullName).Length
        $newSize = (Get-Item $tempFile).Length
        
        if ($newSize -lt $oldSize -or $ext -eq ".heic") {
            $reduction = [math]::Round((($oldSize - $newSize) / $oldSize) * 100, 2)
            
            # Si era HEIC, eliminamos el original y guardamos el JPG
            if ($ext -eq ".heic") {
                Remove-Item $img.FullName
                Move-Item -Path $tempFile -Destination $destFile -Force
                Write-Host " Convertido a JPG! Reduccin del $reduction%" -ForegroundColor Green
            } else {
                Move-Item -Path $tempFile -Destination $img.FullName -Force
                Write-Host " OK! Reduccin del $reduction%" -ForegroundColor Green
            }
        } else {
            Remove-Item $tempFile
            Write-Host " Saltado" -ForegroundColor Gray
        }
    }
}

Write-Host "`n--- Fase 2 de Optimizacin Completada ---" -ForegroundColor Cyan
Write-Host "Las imgenes gigantes y videos ahora tienen el tamao correcto para la web."

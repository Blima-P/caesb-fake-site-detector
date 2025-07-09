$json = Get-Content -Path "urls_suspeitas.json" | ConvertFrom-Json

if ($json.status -eq "anomalía_detectada") {
    Write-Host "ALERTA: Sites suspeitos detectados em $($json.suspeitas_detectadas_em)"
    foreach ($url in $json.urls_suspeitas) {
        Write-Host "Denunciando: $url"
        Start-Sleep -Seconds 1
        # Aqui simularia o envio real
    }
    Write-Host "Todas as denúncias foram processadas."
} else {
    Write-Host "Nenhuma anomalia detectada. Nenhuma ação necessária."
}

$sw = @{
    schema_version           = "3.2"
    window_source            = "smoke_test"
    cycle_backend_controlled = $true
    step_id                  = "smoke_001"
    cycle                    = "1/1"
    time_source              = "metadata (STRICT_SYNC): PLACEHOLDER"
    prev_window_hash         = "PLACEHOLDER"
    window_hash              = "PLACEHOLDER"
    mcp_trigger              = @{ timestamp = "PLACEHOLDER" }
    goal                     = "Smoke test: V5.0 pipeline end-to-end"
    inputs                   = @{ trigger = "writer_cli"; repo_head = "manual_check" }
    actions                  = @("write_pending_status", "watcher_auto_add", "verify")
    risk                     = @()
    assumptions              = @()
    rule_tangency            = @{ tangency_detected = $false; notes = "smoke" }
    reflection_curve         = @{ delta = ""; correction = ""; next = "Verify chain+hash" }
    output_plan              = @("verify", "inspect_last_entry")
    window_type              = "verification"
    confidence               = 1.0
}
$json = ($sw | ConvertTo-Json -Depth 10 -Compress)
$tmp = [System.IO.Path]::GetTempFileName()
$json | Out-File -FilePath $tmp -Encoding utf8
Get-Content $tmp | python tooling/scripts/automation/write_pending_status.py
Remove-Item $tmp

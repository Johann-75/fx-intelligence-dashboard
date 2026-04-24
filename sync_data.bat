@echo off
echo Starting FX Intelligence Ingestion...
python backend/fx_scheduler.py --period 1mo
pause

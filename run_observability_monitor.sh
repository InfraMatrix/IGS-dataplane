#!/bin/bash

# Copyright © 2025 InfraMatrix. All Rights Reserved.

# SPDX-License-Identifier: BSD-3-Clause

main()
{
    sudo ./IGS_venv/bin/python3 observability/client/metrics_reporter.py &

    sudo prometheus --config.file=observability/server/prometheus_config.yml &

    export GF_DASHBOARDS_DEFAULT_HOME_DASHBOARD_PATH=observability/server/grafana_node_dashboard.json                      ─╯
    export GF_DATASOURCES_URL=http://localhost:9090
    sudo grafana-server --homepath /usr/share/grafana --config=observability/server/grafana.ini &
}

main

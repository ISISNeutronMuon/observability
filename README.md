# Rollout instructions

We recommend you install the following software locally for your CLI (Command Line Interface):

- Helm
- ArgoCD CLI

## Go from nothing to cluster

These instructions will use the files in the `capi` directory in this repo. So navigate to this directory before following CLI commands at STFC-Cloud documentation for a management cluster. The cluster we will be making is self-managed.

Use the capi directory in this repository as your folder that contains the clouds.yaml, and values.yaml files for the helm charts that handle upgrades. The clouds.yaml file will need to be provided by the developer and is in the .gitignore purposefully.

Follow these [instructions here](https://stfc.atlassian.net/wiki/spaces/CLOUDKB/pages/211878034/Cluster+API+Setup) for setting up the cluster on the cloud, currently we make the cluster "manually" not using the bootstrap as it seems to be a little problematic under some circumstances, the only caveat is that there is not intended to be any management cluster and the cluster should self manage (the management cluster just does everything i.e. there is no prod/staging/dev).

TBD: Deploy ArgoCD

TBD: Deploy the app_of_apps

## Design of the cluster

Cluster consists of several components notably:
- Grafana - Alerting and dashboarding
- Loki - Storage of logs
- Tempo - Storage of traces
- Mimir - Storage of metrics

It will be monitored, using the recommendations we have made notably:

- Grafana Alloy (found in gitops/components/alloy)
    - Prometheus
    - OpenTelemetry (Handling logs, and traces)
- Falco (found in gitops/components/falco)

## Where are the alerts for this cluster?

There is a team for this using microsoft teams. Search for, ISIS Observability, and look at the alerts channel to see the alerts.

Other teams or alert methodologies can be used, just add them to Grafana.
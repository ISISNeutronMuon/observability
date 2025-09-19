# Rollout instructions

We recommend you install the following software locally for your CLI (Command Line Interface):

- Helm
- ArgoCD CLI

## Go from nothing to cluster

### Create cluster
These instructions will use the files in the `capi` directory in this repo. So navigate to this directory before following CLI commands at STFC-Cloud documentation for a management cluster. The cluster we will be making is self-managed.

Use the capi directory in this repository as your folder that contains the clouds.yaml, and values.yaml files for the helm charts that handle upgrades. The clouds.yaml file will need to be provided by the developer and is in the .gitignore purposefully.

Follow these [instructions here](https://stfc.atlassian.net/wiki/spaces/CLOUDKB/pages/211878034/Cluster+API+Setup) for setting up the cluster on the cloud, currently we make the cluster "manually" not using the bootstrap as it seems to be a little problematic under some circumstances, the only caveat is that there is not intended to be any management cluster and the cluster should self manage (the management cluster just does everything i.e. there is no prod/staging/dev).

### Install ArgoCD and deploy the app of apps
This section assumes that you have the context setup appropriately in the Kubeconfigs and you are currently managing the management cluster

Install ArgoCD:
```shell
kubectl create namespace argocd
kubectl apply -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml -n argocd
```

Setup ArgoCD CLI: https://argo-cd.readthedocs.io/en/stable/getting_started/#2-download-argo-cd-cli

Get the initial password:
```
argocd admin initial-password -n argocd
```

Login to the UI using the IP of the worker node running the ArgoCD server, and the port defined in the service for ArgoCD as a URL in your web browser. The username is admin, and the password you already have.

Change the password using the user settings to the one in Keeper so everyone who needs the password has it availiable.

Now it is time to watch the entire cluster's software deploy via ArgoCD:
```
kubectl apply -f gitops/apps/app_of_apps/deployment.yml
```

Once the app of apps is deployed it should deploy the gateway, gateway classes, and routing so you should be able to access the ArgoCD interface from here:
https://argocd.observability.isis.rl.ac.uk.

### Create the S3 for Loki (if not present)

Follow the instructions here: https://stfc.atlassian.net/wiki/spaces/CLOUDKB/pages/377421872/S3+On+OpenStack

You will likely have used s3cmd to create the s3 buckets before, if not, please read the document carefully. Ensure bucket location is set to RegionOne. Use the secrets defined in keeper/vault, when prompted.

Create ones called the following if they do not already exist:
loki-s3-isis-observability
loki-ruler-s3-isis-observability
tempo-s3-isis-observability
mimir-s3-isis-observability
mimir-ruler-s3-isis-observability

## Creating new endpoints for new users for Loki, Tempo, and Mimir:

In order to enforce multi-tenancy properly, and limiting damage in-case of leakage of credentials we use basic_auth to automatically add the correct header.

- Create a basic auth secret in Vault. This is a .htpasswd file and has to be done in SHA format using:
```bash
htpasswd -cbs .htpasswd username password
```
  - With this .htpasswd create the secret in vault with the username.
- Create a new HTTPRoute for the endpoint they will be using. (A good example is observability-httproute.yml in Loki)
  - It needs to Rewrite the prefix, and add a unique identifier to the header so it can handle multi-tenancy.
- Create a new SecurityPolicy that uses the auth secret from vault. (A good example is observability-basic-auth.yaml in Loki)
- Repeat this for the other endpoints on Tempo and Mimir as required.
- These are now ready to be used to write to and as a data source in Grafana.
- For Tempo if they would like access to Trace generated metrics (service graphs, span metrics, etc) in Mimir please adjust the Tempo Deployment to facilitate that. It will need the correct remote-write-header set for example: `'X-Scope-OrgID': "Observability"` For example:
```yaml
per_tenant_overrides:
  FASE-prod:
    metrics_generator:
      processors:
        - service-graphs
        - span-metrics
        - local-blocks
      remote_write_headers:
        'X-Scope-OrgID': "FASE-prod"
```
## Elements that are available from this cluster:

ArgoCD: https://argocd.observability.isis.rl.ac.uk

Planned (not implemented):
- Grafana: https://grafana.observability.isis.rl.ac.uk
- Loki: https://loki.observability.isis.rl.ac.uk
- Mimir: https://mimir.observability.isis.rl.ac.uk
- Tempo: https://tempo.observability.isis.rl.ac.uk

https://observability.isis.rl.ac.uk forwards to the Grafana endpoint as that is the most likely interacted with.

## Design of the cluster

Cluster consists of several components notably:
- Grafana - Alerting and dashboarding
    - Backed by a PostgreSQL DB maintained by DB Services
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
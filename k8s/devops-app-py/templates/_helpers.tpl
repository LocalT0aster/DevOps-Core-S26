{{/*
Expand the name of the chart.
*/}}
{{- define "devops-app-py.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "devops-app-py.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "devops-app-py.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "devops-app-py.labels" -}}
helm.sh/chart: {{ include "devops-app-py.chart" . }}
{{ include "devops-app-py.selectorLabels" . }}
{{- if (or .Values.image.tag .Chart.AppVersion) }}
app.kubernetes.io/version: {{ .Values.image.tag | default .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/part-of: {{ .Values.partOf }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "devops-app-py.selectorLabels" -}}
app.kubernetes.io/name: {{ include "devops-app-py.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the service name.
*/}}
{{- define "devops-app-py.serviceName" -}}
{{- printf "%s-service" (include "devops-app-py.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create the secret name.
*/}}
{{- define "devops-app-py.secretName" -}}
{{- printf "%s-secret" (include "devops-app-py.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create the service account name.
*/}}
{{- define "devops-app-py.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "devops-app-py.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Render non-secret environment variables.
*/}}
{{- define "devops-app-py.envVars" -}}
{{- range .Values.env }}
- name: {{ .name }}
  value: {{ .value | quote }}
{{- end }}
{{- end }}

{{/*
Render Vault injector annotations.
*/}}
{{- define "devops-app-py.vaultAnnotations" -}}
{{- if .Values.vault.enabled }}
vault.hashicorp.com/agent-inject: "true"
vault.hashicorp.com/role: {{ .Values.vault.role | quote }}
vault.hashicorp.com/agent-inject-secret-config: {{ .Values.vault.secretPath | quote }}
vault.hashicorp.com/agent-inject-file-config: {{ .Values.vault.templateFile | quote }}
vault.hashicorp.com/agent-inject-template-config: |
  {{ "{{- with secret \"" }}{{ .Values.vault.secretPath }}{{ "\" -}}" }}
  APP_USERNAME={{ "{{ .Data.data.APP_USERNAME }}" }}
  APP_PASSWORD={{ "{{ .Data.data.APP_PASSWORD }}" }}
  APP_API_KEY={{ "{{ .Data.data.APP_API_KEY }}" }}
  {{ "{{- end }}" }}
{{- end }}
{{- end }}

{{/*
Create the pre-install hook job name.
*/}}
{{- define "devops-app-py.preInstallJobName" -}}
{{- printf "%s-pre-install" (include "devops-app-py.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create the post-install hook job name.
*/}}
{{- define "devops-app-py.postInstallJobName" -}}
{{- printf "%s-post-install" (include "devops-app-py.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

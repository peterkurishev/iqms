{{- define "full-name" -}}
{{- if .Values.global.prefix }}{{ .Values.global.prefix }}-{{- end }}{{ .Release.Name }}{{- end }}

{{- define "django-backend.fullname" -}}
{{- if .Values.global.prefix }}{{ .Values.global.prefix }}-{{- end }}django-backend{{- end }}

{{- define "react-frontend.fullname" -}}
{{- if .Values.global.prefix }}{{ .Values.global.prefix }}-{{- end }}react-frontend{{- end }}

{{- define "my-full-stack-app.full-name" -}}
{{- $name := .Chart.Name -}}
{{- $release := .Release.Name -}}
{{- $fullName := printf "%s-%s" $release $name -}}
{{- printf "%s" $fullName -}}
{{- end -}}
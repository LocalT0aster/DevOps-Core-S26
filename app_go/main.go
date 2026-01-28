// DevOps Info Service in Go.
package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net"
	"net/http"
	"os"
	"runtime"
	"strings"
	"time"
)

const (
	serviceName        = "devops-info-service"
	serviceVersion     = "1.0.0"
	serviceDescription = "DevOps course info service"
	serviceFramework   = "Go net/http"
)

type ServiceInfo struct {
	Name        string `json:"name"`
	Version     string `json:"version"`
	Description string `json:"description"`
	Framework   string `json:"framework"`
}

type SystemInfo struct {
	Hostname        string `json:"hostname"`
	Platform        string `json:"platform"`
	PlatformVersion string `json:"platform_version"`
	Architecture    string `json:"architecture"`
	CPUCount        int    `json:"cpu_count"`
	PythonVersion   string `json:"python_version"`
}

type UptimeInfo struct {
	Seconds int64  `json:"seconds"`
	Human   string `json:"human"`
}

type RequestInfo struct {
	ClientIP  string `json:"client_ip"`
	UserAgent string `json:"user_agent"`
	Method    string `json:"method"`
	Path      string `json:"path"`
}

type EndpointInfo struct {
	Path        string `json:"path"`
	Method      string `json:"method"`
	Description string `json:"description"`
}

type RootResponse struct {
	Service   ServiceInfo    `json:"service"`
	System    SystemInfo     `json:"system"`
	Runtime   UptimeInfo     `json:"runtime"`
	Request   RequestInfo    `json:"request"`
	Endpoints []EndpointInfo `json:"endpoints"`
}

type HealthResponse struct {
	Status        string `json:"status"`
	Timestamp     string `json:"timestamp"`
	UptimeSeconds int64  `json:"uptime_seconds"`
}

var (
	// startTime is used for uptime calculations.
	startTime = time.Now().UTC()
	// endpoints is a static list used to mirror the Python app output.
	endpoints = []EndpointInfo{
		{Path: "/", Method: http.MethodGet, Description: "Service information."},
		{Path: "/health", Method: http.MethodGet, Description: "Health check endpoint."},
	}
)

// getServiceInfo returns static service metadata.
func getServiceInfo() ServiceInfo {
	return ServiceInfo{
		Name:        serviceName,
		Version:     serviceVersion,
		Description: serviceDescription,
		Framework:   serviceFramework,
	}
}

// getSystemInfo returns host and runtime information.
func getSystemInfo() SystemInfo {
	hostname, err := os.Hostname()
	if err != nil {
		hostname = "unknown"
	}

	return SystemInfo{
		Hostname:        hostname,
		Platform:        platformName(),
		PlatformVersion: platformVersion(),
		Architecture:    runtime.GOARCH,
		CPUCount:        runtime.NumCPU(),
		PythonVersion:   runtime.Version(),
	}
}

// platformName maps GOOS to a human-readable name.
func platformName() string {
	switch runtime.GOOS {
	case "linux":
		return "Linux"
	case "windows":
		return "Windows"
	case "darwin":
		return "Darwin"
	default:
		return runtime.GOOS
	}
}

// platformVersion attempts to return a friendly OS version.
func platformVersion() string {
	switch runtime.GOOS {
	case "linux":
		if pretty := linuxPrettyName(); pretty != "" {
			return pretty
		}
	case "windows":
		if osName := os.Getenv("OS"); osName != "" {
			return osName
		}
	}

	return runtime.GOOS
}

// linuxPrettyName reads PRETTY_NAME from /etc/os-release if available.
func linuxPrettyName() string {
	data, err := os.ReadFile("/etc/os-release")
	if err != nil {
		return ""
	}

	for _, line := range strings.Split(string(data), "\n") {
		line = strings.TrimSpace(line)
		if strings.HasPrefix(line, "PRETTY_NAME=") {
			value := strings.TrimPrefix(line, "PRETTY_NAME=")
			return strings.Trim(value, "\"")
		}
	}

	return ""
}

// getUptime returns elapsed time since startTime.
func getUptime() UptimeInfo {
	seconds := int64(time.Since(startTime).Seconds())
	hours := seconds / 3600
	minutes := (seconds % 3600) / 60

	return UptimeInfo{
		Seconds: seconds,
		Human:   fmt.Sprintf("%d hours, %d minutes", hours, minutes),
	}
}

// getRequestInfo captures minimal request metadata.
func getRequestInfo(r *http.Request) RequestInfo {
	return RequestInfo{
		ClientIP:  clientIP(r),
		UserAgent: r.Header.Get("User-Agent"),
		Method:    r.Method,
		Path:      r.URL.Path,
	}
}

// clientIP attempts to derive the client IP from proxy headers or RemoteAddr.
func clientIP(r *http.Request) string {
	if forwarded := r.Header.Get("X-Forwarded-For"); forwarded != "" {
		parts := strings.Split(forwarded, ",")
		return strings.TrimSpace(parts[0])
	}

	host, _, err := net.SplitHostPort(r.RemoteAddr)
	if err == nil {
		return host
	}

	return r.RemoteAddr
}

// listEndpoints returns the advertised endpoints for the root response.
func listEndpoints() []EndpointInfo {
	return endpoints
}

// mainHandler serves GET /.
func mainHandler(w http.ResponseWriter, r *http.Request) {
	payload := RootResponse{
		Service:   getServiceInfo(),
		System:    getSystemInfo(),
		Runtime:   getUptime(),
		Request:   getRequestInfo(r),
		Endpoints: listEndpoints(),
	}

	writeJSON(w, http.StatusOK, payload)
}

// healthHandler serves GET /health.
func healthHandler(w http.ResponseWriter, r *http.Request) {
	payload := HealthResponse{
		Status:        "healthy",
		Timestamp:     time.Now().UTC().Format("2006-01-02T15:04:05.000000-07:00"),
		UptimeSeconds: getUptime().Seconds,
	}

	writeJSON(w, http.StatusOK, payload)
}

// notFound returns a JSON 404.
func notFound(w http.ResponseWriter, r *http.Request) {
	writeJSON(w, http.StatusNotFound, map[string]string{
		"error":   "Not Found",
		"message": "Endpoint does not exist",
	})
}

// router dispatches requests to handlers.
func router(w http.ResponseWriter, r *http.Request) {
	switch {
	case r.URL.Path == "/" && r.Method == http.MethodGet:
		mainHandler(w, r)
	case r.URL.Path == "/health" && r.Method == http.MethodGet:
		healthHandler(w, r)
	default:
		notFound(w, r)
	}
}

// recoverMiddleware converts panics into JSON 500 responses.
func recoverMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		defer func() {
			if err := recover(); err != nil {
				log.Printf("panic: %v", err)
				writeJSON(w, http.StatusInternalServerError, map[string]string{
					"error":   "Internal Server Error",
					"message": "An unexpected error occurred",
				})
			}
		}()
		log.Printf("Request: %s %s", r.Method, r.URL.Path)
		next.ServeHTTP(w, r)
	})
}

// writeJSON serializes a payload with the given status code.
func writeJSON(w http.ResponseWriter, status int, payload any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	if err := json.NewEncoder(w).Encode(payload); err != nil {
		log.Printf("encode error: %v", err)
	}
}

func main() {
	host := os.Getenv("HOST")
	if host == "" {
		host = "0.0.0.0"
	}

	port := os.Getenv("PORT")
	if port == "" {
		port = "5000"
	}

	addr := net.JoinHostPort(host, port)
	log.Printf("Application starting on %s", addr)

	handler := recoverMiddleware(http.HandlerFunc(router))
	if err := http.ListenAndServe(addr, handler); err != nil {
		log.Fatalf("server error: %v", err)
	}
}

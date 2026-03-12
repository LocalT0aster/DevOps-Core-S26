package main

import (
	"bytes"
	"encoding/json"
	"io"
	"net/http"
	"net/http/httptest"
	"testing"
)

func captureLogOutput(w io.Writer) func() {
	logMu.Lock()
	previous := logOutput
	logOutput = w
	logMu.Unlock()

	return func() {
		logMu.Lock()
		logOutput = previous
		logMu.Unlock()
	}
}

func decodeLogEntry(t *testing.T, buffer *bytes.Buffer) map[string]any {
	t.Helper()

	lines := bytes.Split(bytes.TrimSpace(buffer.Bytes()), []byte("\n"))
	if len(lines) != 1 {
		t.Fatalf("expected exactly one log line, got %d", len(lines))
	}

	var entry map[string]any
	if err := json.Unmarshal(lines[0], &entry); err != nil {
		t.Fatalf("failed to decode log entry: %v", err)
	}

	return entry
}

func TestRequestLoggingMiddlewareEmitsJSONAccessLog(t *testing.T) {
	var buffer bytes.Buffer
	restore := captureLogOutput(&buffer)
	defer restore()

	handler := requestLoggingMiddleware(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusCreated)
		_, _ = w.Write([]byte(`{"ok":true}`))
	}))

	request := httptest.NewRequest(http.MethodGet, "/health?full=1", nil)
	request.RemoteAddr = "203.0.113.10:4321"
	request.Header.Set("User-Agent", "go-test")

	recorder := httptest.NewRecorder()
	handler.ServeHTTP(recorder, request)

	if recorder.Code != http.StatusCreated {
		t.Fatalf("expected status %d, got %d", http.StatusCreated, recorder.Code)
	}

	entry := decodeLogEntry(t, &buffer)
	if entry["level"] != "INFO" {
		t.Fatalf("expected INFO level, got %#v", entry["level"])
	}
	if entry["logger"] != accessLoggerName {
		t.Fatalf("expected logger %q, got %#v", accessLoggerName, entry["logger"])
	}
	if entry["client_ip"] != "203.0.113.10" {
		t.Fatalf("expected client_ip to be logged, got %#v", entry["client_ip"])
	}
	if entry["method"] != http.MethodGet {
		t.Fatalf("expected method to be logged, got %#v", entry["method"])
	}
	if entry["path"] != "/health" {
		t.Fatalf("expected path to be logged, got %#v", entry["path"])
	}
	if entry["query"] != "?full=1" {
		t.Fatalf("expected query string to be logged, got %#v", entry["query"])
	}
	if entry["status_code"] != float64(http.StatusCreated) {
		t.Fatalf("expected status_code to be logged, got %#v", entry["status_code"])
	}
	if entry["response_bytes"] != "11" {
		t.Fatalf("expected response_bytes to be logged, got %#v", entry["response_bytes"])
	}
	if _, ok := entry["request_time_us"].(float64); !ok {
		t.Fatalf("expected request_time_us to be numeric, got %#v", entry["request_time_us"])
	}
	if entry["user_agent"] != "go-test" {
		t.Fatalf("expected user_agent to be logged, got %#v", entry["user_agent"])
	}
	if _, hasMessage := entry["message"]; hasMessage {
		t.Fatalf("access log should not include message, got %#v", entry["message"])
	}
}

func TestRecoverMiddlewareEmitsJSONPanicLog(t *testing.T) {
	var buffer bytes.Buffer
	restore := captureLogOutput(&buffer)
	defer restore()

	handler := recoverMiddleware(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		panic("boom")
	}))

	request := httptest.NewRequest(http.MethodGet, "/explode", nil)
	request.RemoteAddr = "203.0.113.20:8080"
	request.Header.Set("User-Agent", "go-test")

	recorder := httptest.NewRecorder()
	handler.ServeHTTP(recorder, request)

	if recorder.Code != http.StatusInternalServerError {
		t.Fatalf("expected status %d, got %d", http.StatusInternalServerError, recorder.Code)
	}

	entry := decodeLogEntry(t, &buffer)
	if entry["level"] != "ERROR" {
		t.Fatalf("expected ERROR level, got %#v", entry["level"])
	}
	if entry["logger"] != serviceLoggerName {
		t.Fatalf("expected logger %q, got %#v", serviceLoggerName, entry["logger"])
	}
	if entry["message"] != "request panic recovered" {
		t.Fatalf("expected panic message to be logged, got %#v", entry["message"])
	}
	if entry["error"] != "boom" {
		t.Fatalf("expected panic error to be logged, got %#v", entry["error"])
	}
	if entry["path"] != "/explode" {
		t.Fatalf("expected panic path to be logged, got %#v", entry["path"])
	}
	if entry["query"] != "" {
		t.Fatalf("expected empty query string, got %#v", entry["query"])
	}
	if entry["client_ip"] != "203.0.113.20" {
		t.Fatalf("expected client_ip to be logged, got %#v", entry["client_ip"])
	}
}

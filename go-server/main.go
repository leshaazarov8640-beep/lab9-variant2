package main

import (
    "encoding/binary"
    "encoding/json"
    "fmt"
    "io"
    "log"
    "net/http"
    "os"
    "sync"
    "time"
)

// Структура задачи (Задание 2)
type Task struct {
    ID        int
    Data      []byte
    CreatedAt time.Time
}

// Очередь задач и результаты
var taskQueue = make(chan Task, 100)
var taskCounter int
var mu sync.Mutex
var results = make(map[int][]byte)

// Горутина для фоновой обработки (Задание 2)
func backgroundWorker() {
    for task := range taskQueue {
        log.Printf("Worker: processing task %d", task.ID)
        time.Sleep(2 * time.Second)
        
        // Обработка данных (инверсия битов)
        processed := make([]byte, len(task.Data))
        for i, b := range task.Data {
            processed[i] = ^b
        }
        
        mu.Lock()
        results[task.ID] = processed
        mu.Unlock()
        
        log.Printf("Worker: completed task %d", task.ID)
    }
}

// Структуры для JSON (Задание 4)
type NumbersInput struct {
    Numbers []int `json:"numbers"`
}

type SumOutput struct {
    Sum int `json:"sum"`
}

// Эндпоинт для отправки задачи
func handleProcess(w http.ResponseWriter, r *http.Request) {
    if r.Method != http.MethodPost {
        http.Error(w, "Only POST allowed", http.StatusMethodNotAllowed)
        return
    }

    data, err := io.ReadAll(r.Body)
    if err != nil {
        http.Error(w, "Failed to read body", http.StatusBadRequest)
        return
    }
    defer r.Body.Close()

    mu.Lock()
    taskCounter++
    taskID := taskCounter
    mu.Unlock()

    taskQueue <- Task{
        ID:        taskID,
        Data:      data,
        CreatedAt: time.Now(),
    }

    // Возвращаем ID задачи в бинарном формате
    response := make([]byte, 8)
    binary.LittleEndian.PutUint64(response, uint64(taskID))
    w.Header().Set("Content-Type", "application/octet-stream")
    w.WriteHeader(http.StatusAccepted)
    w.Write(response)
}

// Эндпоинт для получения результата
func handleResult(w http.ResponseWriter, r *http.Request) {
    if r.Method != http.MethodGet {
        http.Error(w, "Only GET allowed", http.StatusMethodNotAllowed)
        return
    }

    taskIDStr := r.URL.Query().Get("id")
    if taskIDStr == "" {
        http.Error(w, "Missing task ID", http.StatusBadRequest)
        return
    }

    var taskID int
    fmt.Sscanf(taskIDStr, "%d", &taskID)

    mu.Lock()
    result, exists := results[taskID]
    mu.Unlock()

    if !exists {
        http.Error(w, "Task not found", http.StatusNotFound)
        return
    }

    w.Header().Set("Content-Type", "application/octet-stream")
    w.Write(result)
}

func main() {
    // Задание 4: Проверка режима JSON через stdin
    stat, _ := os.Stdin.Stat()
    if (stat.Mode() & os.ModeCharDevice) == 0 {
        // Режим подпроцесса - обрабатываем JSON
        var input NumbersInput
        err := json.NewDecoder(os.Stdin).Decode(&input)
        if err != nil {
            log.Fatal("JSON decode error:", err)
        }

        sum := 0
        for _, n := range input.Numbers {
            sum += n * n
        }

        json.NewEncoder(os.Stdout).Encode(SumOutput{Sum: sum})
        return
    }

    // Задание 2: Запуск HTTP сервера с горутиной
    go backgroundWorker()
    
    http.HandleFunc("/process", handleProcess)
    http.HandleFunc("/result", handleResult)
    
    log.Println("HTTP server starting on :8080")
    log.Fatal(http.ListenAndServe(":8080", nil))
}
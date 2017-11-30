language: PYTHON
name: "cherrypick2_offline"

variable {
    name: "cpu_count"
    type: ENUM
    size: 1
    options: "1"
    options: "2"
    options: "4"
    options: "8"
}

variable {
    name: "root_disk"
    type: ENUM
    size: 1
    options: "2"
    options: "5"
    options: "10"
    options: "20"
    options: "40"
    options: "80"
    options: "160"
}

variable {
    name: "machine_count"
    type: INT
    size: 1
    min: 2
    max: 8
}


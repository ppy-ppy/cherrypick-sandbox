language: PYTHON
name: "local"

variable {
    name: "vm_type"
    type: ENUM
    size: 1
    options: "r2"
    options: "c3"
    options: "d1"
}

variable {
    name: "vm_size"
    type: ENUM
    size: 1
    options: "nano"
    options: "micro"
    options: "tiny"
    options: "small"
    options: "medium"
    options: "large"
    options: "xlarge"
}

variable {
    name: "machine_count"
    type: INT
    size: 1
    min: 2
    max: 8
}


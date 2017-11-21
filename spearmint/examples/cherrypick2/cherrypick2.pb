language: PYTHON
name: "cherrypick2_offline"

variable {
    name: "vm_type"
    type: ENUM
    size: 1
    options: "m4"
    options: "r3"
    options: "c4"
    options: "i2"
}

variable {
    name: "cpu_count"
    type: ENUM
    size: 1
    options: "2"
    options: "4"
    options: "8"
}

variable {
    name: "machine_count"
    type: INT
    size: 1
    min: 2
    max: 7
}


function setMinuteToZero(input) {
    var selectedTime = input.value;
    var parts = selectedTime.split(':');
    // Đặt số phút thành 00
    parts[1] = '00';
    // Kết hợp lại thành chuỗi thời gian mới
    var newTime = parts.join(':');
    // Đặt giá trị của ô chọn thời gian thành thời gian mới
    input.value = newTime;
}

function checkFileSize() {
    var totalSize = 0;
    var fileInput = document.getElementById('id_files');
    var fileList = [];

    // Loop through each selected file
    for (var i = 0; i < fileInput.files.length; i++) {
        totalSize += fileInput.files[i].size; // Add the size of each file
        fileList.push({ name: fileInput.files[i].name, size: fileInput.files[i].size });
    }

    // Check if total size exceeds 5MB
    if (totalSize > 5 * 1024 * 1024) { // 5MB in bytes
        // Sort the file list by size in descending order
        fileList.sort(function (a, b) {
            return b.size - a.size;
        });

        var remainingSize = totalSize;
        var i = 0;

        while (i < fileList.length && remainingSize > 5 * 1024 * 1024) {
            remainingSize -= fileList[i].size;
            i++;
        }

        var message = "Общий размер файла превышает 5 МБ. Самые большие файлы в письме будут отправлены ссылкой:";
        // Construct a list of largest files that do not fit
        for (var j = 0; j < i; j++) {
            message += "<br>" + fileList[j].name + " (" + formatFileSize(fileList[j].size) + ")";
        }

        // Display the message in a toast
        $.toast({
            message: message,
            showIcon: 'warning',
            class: 'warning',
            displayTime: 10000
        });
        // $('.ui.toast').toast('show');
    }
}

// Function to format file size in human-readable format
function formatFileSize(size) {
    if (size < 1024) {
        return size + ' bytes';
    } else if (size < 1024 * 1024) {
        return (size / 1024).toFixed(2) + ' KB';
    } else {
        return (size / (1024 * 1024)).toFixed(2) + ' MB';
    }
}
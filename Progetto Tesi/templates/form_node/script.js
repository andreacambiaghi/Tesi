var inputCount = 2;
var inputs = [];

document.getElementById('add-btn').addEventListener('click', function() {
    inputCount++;
    var inputGroup = document.createElement('div');
    inputGroup.className = 'input-group';
    inputGroup.innerHTML = '<input type="text" id="input' + inputCount + '" value="">';

    document.getElementById('input-container').appendChild(inputGroup);
    if (inputCount > 2) {
        document.getElementById('remove-btn').classList.remove('disabled');
    }
});

document.getElementById('remove-btn').addEventListener('click', function() {
    if (inputCount > 2) {
        var inputContainer = document.getElementById('input-container');
        var lastInputGroup = inputContainer.lastChild;
        inputContainer.removeChild(lastInputGroup);
        inputCount--;
        if (inputCount === 2) {
            document.getElementById('remove-btn').classList.add('disabled');
        }
    }
});

document.getElementById('save-btn').addEventListener('click', function() {
    var nodeName = document.getElementById('node-name').value;
    var nodeType = document.getElementById('node-type').value;
    var outputs = [];
    for (var i = 1; i <= inputCount; i++) {
        var inputValue = document.getElementById('input' + i).value;
        outputs.push(inputValue);
    }

    // Validazione dei campi
    if (nodeName === '' || nodeType === '' || outputs.some(output => output === '')) {
        alert('Per favore, compila tutti i campi prima di salvare.');
        return;
    }

    alert("Nome Nodo: " + nodeName + "\nTipo Nodo: " + nodeType + "\nOutputs: " + outputs.join(", "));

    document.getElementById('node-name').value = '';
    document.getElementById('node-type').value = '';
    for (var i = 1; i <= inputCount; i++) {
        document.getElementById('input' + i).value = '';
    }
    inputCount = 2;
    document.getElementById('input-container').innerHTML = '';
    document.getElementById('add-btn').classList.remove('disabled');
    document.getElementById('remove-btn').classList.add('disabled');
});
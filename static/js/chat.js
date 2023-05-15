let previousUsername = document.getElementById('previousUsername').getAttribute('data-value');
var current_user_login = document.getElementById('current_user_login').getAttribute('data-value');
$(document).ready(function() {
    $('.card-body').scrollTop($('.card-body')[0].scrollHeight);
    var socket = io.connect('http://' + document.domain + ':' + location.port);

    socket.on('connect', function() {
        socket.emit('join', {'username': current_user_login});
    });

    var inputTextField = document.getElementById('message-input');
    var timer;
    var typing = false;
    var timer_typing;
    var typing_users = [];

    // Добавить пользователя в список печатающих
    function addUserTyping(username) {
        if (!typing_users.includes(username)) {
            typing_users.push(username);
            updateTypingIndicator();
        }
    };

    // Удалить пользователя из списка печатающих
    function removeUserTyping(username) {
        var index = typing_users.indexOf(username);
        if (index !== -1) {
            typing_users.splice(index, 1);
            updateTypingIndicator();
        }
    };

    // Обновить индикатор печати
    function updateTypingIndicator() {
        var indicatorText = '';
        var typing_users_without_me = typing_users.filter(function (item) {
            return item != current_user_login;
        });
        if (typing_users_without_me.length == 1) {
            indicatorText = typing_users_without_me.join('') + ' печатает...';
        } else if (typing_users_without_me.length > 1) {
            indicatorText = typing_users_without_me.join(', ') + ' печатают...';
        }
        $('#typing-indicator').text(indicatorText);
};

    inputTextField.oninput = function() {
        if (typing === true) {
            return
        }
        socket.emit('typing', {username: current_user_login});
        typing = true;

        clearTimeout(timer);
        clearTimeout(timer_typing);
        timer_typing = setTimeout(function() {
            typing = false
        }, 2800)
        timer = setTimeout(function() {
            typing = false;
            socket.emit('stop-typing', {username: current_user_login});
        }, 3000)
    };

    socket.on('typing', function(data) {
        addUserTyping(data.username)
    });

    socket.on('stop-typing', function(data) {
        removeUserTyping(data.username)
    });

    socket.on('message', function(data) {
        var date = new Date();
        var formattedTime = date.toLocaleTimeString('ru-RU', { hour: 'numeric', minute: 'numeric' });
        var messageClass = (data.username === current_user_login) ? 'my-message-container' : 'other-message-container';
        var boxClass = 'message-box';
        // Если имя пользователя не совпадает с предыдущим сообщением, то добавляем его в разметку
        if (data.username !== previousUsername) {
            var username = '<span class="username">' + data.username + '</span>';
        } else {
            var username = '';
            var boxClass = 'message-box-noauthor';
        }
        var message = '<div class="' + messageClass + '">' + username + '<div class="' + boxClass + '"><span class="chat-message">' + data.message + '</span></div><span class="timestamp">' + formattedTime + '</span></div>';
        $('.card-body').append(message);
        $('.card-body').scrollTop($('.card-body')[0].scrollHeight);

        previousUsername = data.username;
    });

    $('#message-form').submit(function(event) {
        event.preventDefault();
        var message = $('#message-input').val();  // Извлекаем значение из формы
        if (message == '') {
            return;
        }
        socket.emit('send_message', {'message': message});  // Передаем сообщение на сервер
        $('#message-input').val('');  // Очищаем форму после отправки
        socket.emit('stop-typing', {username: current_user_login});
    });
    
    $('#message-input').keypress(function(event) {
        if (event.which == 13) {
        event.preventDefault();
        $('#message-form').submit();
        }
    });
});
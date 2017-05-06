var pathArray = window.location.pathname.split('/');
var query = window.location.search;
var page = parseInt(pathArray[2]);
var pageString = "/page/";

var next = page + 1;
var prev = page - 1;

if (prev < 1) {
    prev = 1;
}

if (isNaN(page)) {
    next = 2;
    prev = 1;
}

if (query != "") {
    pageString = "/search/";
}

var maxId = 5;
for (var i = 0; i < maxId; i++) {
    var el = document.getElementById('page-' + i), n = prev + i;
    if (el == null)
        continue;
    el.href = pageString + n + query;
    el.innerHTML = n;
}

var e = document.getElementById('page-next');
if (e != null)
    e.href = pageString + next + query;
var e = document.getElementById('page-prev');
if (e != null)
    e.href = pageString + prev + query;

// Used by spoiler tags
function toggleLayer(elem) {
    if (elem.classList.contains("hide"))
        elem.classList.remove("hide");
    else
        elem.classList.add("hide");
}

function formatDate(date) { // thanks stackoverflow
    var monthNames = [
        "January", "February", "March",
        "April", "May", "June", "July",
        "August", "September", "October",
        "November", "December"
    ];

    var day = date.getDate();
    var monthIndex = date.getMonth();
    var year = date.getFullYear();

    return day + ' ' + monthNames[monthIndex] + ' ' + year;
}

var list = document.getElementsByClassName("date-short");
for (var i in list) {
    var e = list[i];
    e.title = e.innerText;
    e.innerText = formatDate(new Date(e.innerText));
}

var list = document.getElementsByClassName("date-full");
for (var i in list) {
    var e = list[i];
    e.title = e.innerText;
    var date = new Date(e.innerText);
    e.innerText = date.toDateString() + " " + date.toLocaleTimeString();
}


$(function () {
    $('.button-checkbox').each(function () {
        var $widget = $(this),
            $button = $widget.find('button'),
            $checkbox = $widget.find('input:checkbox'),
            color = $button.data('color'),
            settings = {
                on: {
                    icon: 'glyphicon glyphicon-check'
                },
                off: {
                    icon: 'glyphicon glyphicon-unchecked'
                }
            };

        $button.on('click', function () {
            $checkbox.prop('checked', !$checkbox.is(':checked'));
            $checkbox.triggerHandler('change');
            updateDisplay();
        });

        $checkbox.on('change', function () {
            updateDisplay();
        });

        function updateDisplay() {
            var isChecked = $checkbox.is(':checked');
            // Set the button's state
            $button.data('state', (isChecked) ? "on" : "off");

            // Set the button's icon
            $button.find('.state-icon')
                .removeClass()
                .addClass('state-icon ' + settings[$button.data('state')].icon);

            // Update the button's color
            if (isChecked) {
                $button
                    .removeClass('btn-default')
                    .addClass('btn-' + color + ' active');
            }
            else {
                $button
                    .removeClass('btn-' + color + ' active')
                    .addClass('btn-default');
            }
        }

        function init() {
            updateDisplay();
            // Inject the icon if applicable
            if ($button.find('.state-icon').length == 0) {
                $button.prepend('<i class="state-icon ' + settings[$button.data('state')].icon + '"></i> ');
            }
        }

        init();
    });
});
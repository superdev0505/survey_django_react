/**
 * @module Survey
 */

const SV = {

    state: {},

    fetch: (request, body) => fetch(request, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify(body)
        })
        .then(r => {
            let json = r.json();
            if (!r.ok) {
                return json.then(Promise.reject.bind(Promise));
            }
            return json;
        }),

    is_guest: () => {
        let provider = $('#login-link').attr('data-provider');
        return !provider
    },

    is_authorized: () => {
        let el = $('#login-link');
        return el.attr('data-authorized');
    },

    getCSRFToken: () =>
        document.cookie
            .split(';')
            .map(c => c.split('='))
            .find(c => c[0].trim() === 'csrftoken')[1],

    copyToClipboard: (element, value) => {
        let clipboard = document.createElement("input");
        document.body.appendChild(clipboard);
        clipboard.value = value || element && element.innerText;
        clipboard.select();
        document.execCommand("copy");
        clipboard.remove();
    },

    showMessage: (message) => {
        let warning = $('#sc-warning');
        warning.text(message);
        warning.show();
        return setTimeout(() => warning.hide(), 3000)
    },

    showModal: (modalId) => {
        let allModals = document.querySelectorAll('.modal');
        let activeModals = Array.from(allModals).filter(m => m.style.display !== 'none' && m.style.display !== '');
        if (!activeModals.length) {
            return $(modalId).modal('show');
        }
    },

    mc: [],

    kd: [],
};

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.ref-link').forEach(el => {
        el.addEventListener('click', e => {
            SV.copyToClipboard(e, e.target.dataset.link);
            document.dispatchEvent(new Event('copyToClipboard'))
        })
    });

    $('[data-toggle="popover"]').popover();

    let error = window.location.hash.match(/^#error=(.+)/);
    if (error) {
        switch (error[1]) {
            case 'survey_many_answers':
                return SV.showMessage('You can choose only 3 answers maximum')
        }
    }
});

document.addEventListener('copyToClipboard', () => {
    let popup = $('.sc-popup-event').show();
    setTimeout(() => popup.hide(), 2000)
});

let mm = new Set();
document.addEventListener('mousemove', (e) => mm.add(e.clientX + '-' + e.clientY));
document.addEventListener('mousedown', (e) => SV.mc.push(e.clientX + '-' + e.clientY));
document.addEventListener('keydown', (e) => SV.kd.push(e.key));
setTimeout(() => {
    SV.fetch('/analytics/',{m: Array.from(mm), s: document.getElementById('ssm').innerText})
}, 5000);
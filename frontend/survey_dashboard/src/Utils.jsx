
export default class Utils {

    static IP_REGEX = '^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]).){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$';

    /**
     * @param n {Number}
     * @param string {String}
     * @returns {*|string}
     */
    static trunc (n, string) {
        return string && (string.length > n ? string.substr(0, n - 1) + '...' : string);
    }

    /**
     * @param date {Date}
     * @returns {string}
     */
    static formatDate(date) {
        if (!(date instanceof Date)) {
            date = new Date(date)
        }

        return date.getFullYear() + '-'
            + ('0' + (date.getMonth()+1)).slice(-2) + '-'
            + ('0' + date.getDate()).slice(-2)
    }

    /**
     * @param date {Date}
     * @returns {string}
     */
    static formatDateMonthTime(date) {
        return ('0' + (date.getMonth()+1)).slice(-2) + '-'
            + ('0' + date.getDate()).slice(-2) + ' '
            + ('0' + date.getHours()).slice(-2) + ':'
            + ('0' + date.getMinutes()).slice(-2)
    }

    /**
     * @param date {Date}
     * @returns {string}
     */
    static formatDateTime(date) {
        return date.getFullYear() + '-'
            + ('0' + (date.getMonth()+1)).slice(-2) + '-'
            + ('0' + date.getDate()).slice(-2) + 'T'
            + ('0' + date.getHours()).slice(-2) + ':'
            + ('0' + date.getMinutes()).slice(-2)
    }

    /**
     * Simply replace python server time format (2017-12-02T00:00:00) to HumanReadable (2017-12-02 00:00:00)
     * @param dateString {String}
     */
    static formatDateT(dateString) {
        return String(dateString).replace('T', ' ').replace('Z','');
    }

    static formatDateTmills(dateString) {
        return String(dateString).replace('T', ' ').replace('Z','').replace(/\..+/, '');
    }

    static dayOfWeek(day) {
        return ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'][day]
    }

    static monthOfYear(month) {
        return ['January','February','March','April','May','June','July','August','September','October','November','December'][month]
    }

    /**
     * @param stringDateA {String}
     * @param stringDateB {String}
     * @returns {number}
     */
    static sortByDateString(stringDateA, stringDateB) {
        try {
            return new Date(stringDateA).getTime() - new Date(stringDateB).getTime();
        } catch (e) {
            return -1;
        }
    }

    /**
     * @param a {String}
     * @param b {String}
     * @returns {number}
     */
    static sortByNumberOrString(a, b) {
        try {
            if (typeof a === 'number' && typeof b ==='number') {
                return a-b;
            }

            a = String(a).toUpperCase();
            b = String(b).toUpperCase();
            if (a < b) {
                return -1;
            }
            if (a > b) {
                return 1;
            }
            return 0;
        } catch (e) {
            return -1;
        }
    }

    static scrollToTop() {
        if (window.scrollY!==0) {
            setTimeout(function() {
                window.scrollTo(0,window.scrollY-30);
                Utils.scrollToTop();
            }, 10);
        }
    }

    /**
     * Check value is IP
     * @param ip {string}
     * @returns {*|boolean}
     */
    static isIP(ip) {
        return new RegExp(Utils.IP_REGEX).test(ip);
    }

    /**
     * @returns {boolean}
     */
    static isMobile() {
        var check = false;
        (function(a){if(/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up.(browser|link)|vodafone|wap|windows ce|xda|xiino/i.test(a)||/1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw-(n|u)|c55\/|capi|ccwa|cdm-|cell|chtm|cldc|cmd-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc-s|devi|dica|dmob|do(c|p)o|ds(12|-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(-|_)|g1 u|g560|gene|gf-5|g-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd-(m|p|t)|hei-|hi(pt|ta)|hp( i|ip)|hs-c|ht(c(-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i-(20|go|ma)|i230|iac( |-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|-[a-w])|libw|lynx|m1-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|-([1-8]|c))|phil|pire|pl(ay|uc)|pn-2|po(ck|rt|se)|prox|psio|pt-g|qa-a|qc(07|12|21|32|60|-[2-7]|i-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h-|oo|p-)|sdk\/|se(c(-|0|1)|47|mc|nd|ri)|sgh-|shar|sie(-|m)|sk-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h-|v-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl-|tdg-|tel(i|m)|tim-|t-mo|to(pl|sh)|ts(70|m-|m3|m5)|tx-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas-|your|zeto|zte-/i.test(a.substr(0,4)))check = true})(navigator.userAgent||navigator.vendor||window.opera);
        return check;
    }

    /**
     * @returns {string}
     */
    static htmlDecode(value) {
        return String(value)
            .replace(/lt/g, '<')
            .replace(/gt/g, '>')
            .replace(/eq/g, '=')
            .replace(/le/g, '<=')
            .replace(/ge/g, '>=');
    }

    static formatString(str, args) {
        return str.replace(/{(\d+)}/g, function(match, number) {
            return typeof args[number] !== 'undefined'
                ? args[number]
                : match
                ;
        });
    }

    static getColorByScore(score) {
        return Utils.COLOR_GRADIENT[parseInt(score)]
    }

    static debounce = (func, delay) => {
        let inDebounce;
        return function() {
            const context = this;
            const args = arguments;
            clearTimeout(inDebounce);
            inDebounce = setTimeout(() => func.apply(context, args), delay)
        }
    };

    /**
     * @param value
     * @param valueType
     * @returns {*}
     * @throws {SyntaxError} wrong parsed list/dict value
     */
    static toPythonType(value, valueType) {
        switch (valueType) {
            case 'int':
                value = parseInt(value);
                return isNaN(value) ? 0 : Math.floor(value);
            case 'float':
                value = parseFloat(value);
                return isNaN(value) ? 0 : value;
            case 'bool':
                return Boolean(value);
            case 'list':
                return Array.from(JSON.parse(value));
            case 'dict':
                return JSON.parse(value);
            default:
                return value
        }
    }

    /**
     * @param value
     * @param valueType
     * @returns {*}
     * @throws {SyntaxError} wrong parsed list/dict value
     */
    static fromPythonType(value, valueType) {
        switch (valueType) {
            case 'int':
                return String(value);
            case 'float':
                return String(value);
            case 'bool':
                return String(value);
            case 'list':
                return JSON.stringify(value);
            case 'dict':
                return JSON.stringify(value);
            default:
                return value
        }
    }

    /**
     * Pure throttle implementation
     **/
    static throttled = (fn, timeout) => {
        let task, queue = [];
        let lastTaskTime;

        return function() {
            let args = arguments;
            queue.push(fn);

            function next() {
                if (lastTaskTime && ((new Date().getTime() - lastTaskTime) < timeout)) {
                    setTimeout(() => next(), timeout)
                } else {
                    lastTaskTime = new Date().getTime();
                    task = queue[0];
                    queue.shift();
                    return task.apply(this, args);
                }
            }
            return next();
        }
    };

    /**
     * Downloads CSV file for provided array
     * @param data
     * @param filename
     */
    static downloadCSV = (data, filename) => {
        let pom = document.createElement('a');
        let blob = new Blob([data.join('\n')],{type: 'text/csv;charset=utf-8;'});
        pom.href = URL.createObjectURL(blob);
        pom.setAttribute('download', filename || 'report.csv');
        pom.click();
    }

}
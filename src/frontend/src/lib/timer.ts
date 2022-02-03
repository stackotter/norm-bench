export const startTimer = (callback, start: number | null) => {
    if (start == null || start == undefined) {
        start = Date.now();
    }
    var timer: NodeJS.Timer;
    timer = setInterval(() => {
        let clock = Date.now() - start;
        var date = new Date(clock);

        var hours: string | number = date.getUTCHours();
        var minutes: string | number = date.getUTCMinutes();
        var seconds: string | number = date.getSeconds();
        var milliseconds: string | number = date.getMilliseconds();
        
        var string = "";
        
        if (hours > 0) {
            if (hours < 10) { hours = "0" + hours }
            string += hours + ":";
        }

        if (minutes < 10) { minutes = "0" + minutes }
        string += minutes + ":";

        if (seconds < 10) { seconds = "0" + seconds }
        string += seconds + ".";

        if (milliseconds < 100) { milliseconds = "0" + milliseconds }
        if (milliseconds < 10) { milliseconds = "0" + milliseconds }
        string += milliseconds

        callback(string);
    }, 10);
    return timer;
}
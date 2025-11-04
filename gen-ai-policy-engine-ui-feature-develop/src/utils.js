export const msToHms = (timestamp) =>  {
    var m = Math.floor(timestamp % 3600000 / 60000);
    var s = Math.floor(timestamp % 3600000 % 60000 / 1000);

    var mDisplay = m > 0 ? m + (m === 1 ? " minute, " : " minutes, ") : "";
    var sDisplay = s > 0 ? s + (s === 1 ? " second" : " seconds") : "";
    return mDisplay + sDisplay; 
}

export const getTimeRemain = (ttl) => {
    return msToHms(ttl - Date.now())
}  


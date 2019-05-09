var getGuid = function () {
    return createGuid() + createGuid() + "-" + createGuid() + "-" + createGuid() + createGuid() + "-" + createGuid() + createGuid() + createGuid(); //CreateGuid();
}
var createGuid = function () {
    return (((1 + Math.random()) * 0x10000) | 0).toString(16).substring(1);
}
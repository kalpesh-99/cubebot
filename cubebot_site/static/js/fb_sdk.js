
window.fbAsyncInit = function() {
    FB.init({
        appId      : '1863368713926932',
        cookie     : true,
        xfbml      : true,
        version    : 'v2.8'
    });
   //  FB.getLoginStatus(function(response) {
   //    statusChangeCallback(response);
   //  });
};

// Load the SDK Asynchronously
(function(d, s, id) {
    var js, fjs = d.getElementsByTagName(s)[0];
    if (d.getElementById(id)) return;
    js = d.createElement(s); js.id = id;
    js.src = "//connect.facebook.net/en_US/sdk.js";
    fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));

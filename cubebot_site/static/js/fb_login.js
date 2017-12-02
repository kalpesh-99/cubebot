// script to handle login for facebook

function FBlogin() {
    FB.login(function (response) {

        var obj = {
            userID: response.authResponse.userID,
            accessToken: response.authResponse.accessToken
        };


        $.ajax({
            type: "POST",
            url: "/API_FB_login",
            data: JSON.stringify(obj),
            dataType: "json",
            async: false,
            contentType: "application/json",
            success: function (data, textStatus, jqXHR) {
                if (data == "11") {
                    FB.api('/me', function(response) {
                    console.log('Successful login for: ' + response.name);
                    document.getElementById('status').innerHTML =
                      'Thanks for logging in, ' + response.name + '!';
                    });
                    location.replace("/library");

                }
            }
        });

    }, {
        scope: 'public_profile,email,user_friends',
        return_scopes: true
    });
};


function testAPI() {
   console.log('Welcome!  Fetching your information.... ');
   FB.api('/me', function(response) {
     console.log('Successful login for: ' + response.name);
     document.getElementById('status').innerHTML =
       'Thanks for logging in, ' + response.name + '!';
       
   });
 };

function statusChangeCallback(response) {
  console.log('statusChangeCallback');
  console.log(response);
  // The response object is returned with a status field that lets the
  // app know the current login status of the person.
  // Full docs on the response object can be found in the documentation
  // for FB.getLoginStatus().
  if (response.status === 'connected') {
    // Logged into your app and Facebook.
    testAPI();
  } else if (response.status === 'not_authorized') {
        FBlogin();
        console.log("Please log into this app.")
  }  else {
    // The person is not logged into your app or we are unable to tell.
        FBlogin();
        console.log("Please log into this Facebook.")
  }
};



function checkLoginState() {
  FB.getLoginStatus(function(response) {
    console.log(response);
    statusChangeCallback(response);
  });
}

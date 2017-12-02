$(".share-button").click(function() {

  // var tracker = parseInt($("#tracker").text());
  // var sharingID = $(this).parent().closest("p").attr('id');
  var sharingID = $(this).prevAll('p.tracker').attr('id');
  var sharingPSID = resPSID;
  var sharingTID = resTID;
  var sharingType = resTYPE;
  var myName = '{{ current_user.FBname }}';
  alert(myName);

  var thoughtsOnUri = "https://4425ff68.ngrok.io/content/reviewson/" +sharingID;
  var queryString = "?fbName=" +myName +"&userID=" +sharingPSID +"&reviewer=" +sharingTID;
  alert(queryString);
  var thoughtsOnUrl = thoughtsOnUri+queryString;
  alert(thoughtsOnUrl);

  alert(sharingID);
  alert(sharingPSID);
  alert(sharingTID);
  alert(sharingType);
  alert(thoughtsOnUrl);
  console.log(thoughtsOnUrl);

  // alert(tracker);

  // var title = $(this).parent('.tracker').attr('id');
  var title = $(this).prevAll('h3.shareTitle').text();
  // alert(title);
  var url = $(this).prevAll('div.shareURL').text();
  // alert(url);
  var imageUrlPrimary = $(this).prevAll().find('img.getImage').attr('src');
  var imageUrlSecondary = $(this).prevAll('img.getImage').attr('src');
  // alert(imageUrlPrimary);
  // alert(imageUrlSecondary);

  var imageUrl = imageUrlPrimary;

  if (imageUrl == null){
    imageUrl = imageUrlSecondary;
    }

  if (imageUrl == "/static/images/link_building.png"){
    imageUrl = "";
    }


  alert(imageUrl + " ...using this one");
// might be a better way to ensure we select the img url correctly, regardless of positioning

  var data = {
    "file": sharingID,
    "psid": sharingPSID,
    "thread_id" : sharingTID,
    "thread_type": sharingType,
    // "image_url2": imageUrl // just console testing for messenger share
  };
  alert(data);

  var messageToShare = {
        "attachment":{
           "type":"template",
           "payload":{
               "template_type":"generic",
               "elements": [{
                 "title": 'Thoughts On: ' +title,
                 "image_url": imageUrl,
                //  "subtitle": "On the pitch celebrations from Stanford Bridge",
                 "default_action":{
                     "type":"web_url",
                     "url": thoughtsOnUrl
                   },
                   "buttons":[{
                     "type":"web_url",
                     "url":thoughtsOnUrl,
                     "title":"What do you think?"
                   }]
               }]
           }
        }
      };


// This will send data directly to FB Messenger server
  MessengerExtensions.beginShareFlow(function success(response) {
    // Share successful
    if (response.is_sent) {

          $.ajax({
              type : "POST",
              url : "/_load_ajax",
              data: JSON.stringify(data),
              contentType: 'application/json',
              success: function(result) {
                console.log(result);
                // $("#post-success").show();
              },

              error: function(error) {
                console.log(error);
              },

          }),
          alert(data);

          MessengerExtensions.requestCloseBrowser(function success() {


         }, function error(err) {

         });
      }
    }, function error(errorCode, errorMessage) {
    // The user was not able to share

    },
    messageToShare,
    "current_thread");

// alert("something");
});


// testing js function well not jquery;)

// $("#test-button").click(function() {
//   alert("kali did this!")
// });

$("#test-button").click(function() {
  var data = {
    "attachment":{
       "type":"template",
       "payload":{
           "template_type":"generic",
           "elements": [{
               "title":"Chelsea FC: 2017 Champions ",
               "image_url": "https://i.ytimg.com/vi/JrLeyjQO560/maxresdefault.jpg",
               "subtitle": "On the pitch celebrations from Stanford Bridge",
               "default_action":{
                   "type":"web_url",
                   "url": "http://www.chelseafc.com/"
               },
               "buttons":[{
                   "type":"web_url",
                   "url":"https://twitter.com/search?q=chelsea&src=typd",
                   "title":"Twitter q='Chelsea'"
                  },
                  {
                       "type":"web_url",
                       "url":"https://www.youtube.com/results?search_query=chelsea",
                       "title":"YouTube q='Chelsea'"
                   }]
           }]
       }
    }
  };

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

  });
});

// to handle the FB Message Share to Thread
var messageToShare = {
  "attachment":{
     "type":"template",
     "payload":{
         "template_type":"generic",
         "elements": [{
             "title":"I took Peter's 'Which Hat Are You?' Quiz",
             "image_url": "https://bot.peters-hats.com/img/hats/fez.jpg",
             "subtitle": "My result: Fez",
             "default_action":{
                 "type":"web_url",
                 "url": "https://bot.peters-hats.com/view_quiz_results.php?user=24601"
             },
             "buttons":[{
                 "type":"web_url",
                 "url":"https://bot.peters-hats.com/hatquiz.php?referer=24601",
                 "title":"Take the Quiz"
             }]
         }]
     }
  }
};

function placeFBCall() {
  MessengerExtensions.beginShareFlow(function success(response) {
    // Share successful

    }, function error(errorCode, errorMessage) {
    // The user was not able to share

    },
    messageToShare,
    "current_thread");

};

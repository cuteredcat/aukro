var enableTimeout;

$(document).ready(function() {
  $("form.load-seller-rating").on("submit", function(e) {
    // prevent sending the form to the server
    e.preventDefault();

    var seller_id = $("form.load-seller-rating input[name='seller_id']").val(),
        count = $("form.load-seller-rating input[name='count']:checked").val();

    // prevent from submit again
    $("form.load-seller-rating button[type='submit']").prop('disabled', true);

    // prevent from export to excel
    $("form.load-seller-rating a.export").hide();

    // table must be empty
    $("#items tbody tr").remove();

    // show table
    $("#items").show();

    // get requested info
    $.ajax({
      url: "/ajax/seller/" + seller_id + "/list/" + count + "/"
    }).done(function(data) {
      if ("error" in data) {
        alert(data["error"]["reason"] + "\n" + data["error"]["details"]);
      }
      else {
        var links = [];
        for (var i = 0, len = data["result"].length; i < len; i++) {
          var current = data["result"][i],
              datetime = current["datetime"],
              item = current["item"],
              link = current["link"],
              row = $(
                '<tr>' +
                '<td class="datetime">' + datetime + '</td>' +
                '<td class="name"></td>' +
                '<td class="price"></td>' +
                '</tr>'
              ).addClass('item').attr('link', links.length).data('link', link);

          $("#items tbody").append(row);
          links[links.length] = link;
        }

        for (var i = 0, len = links.length; i < len; i++) {
          var link = links[i];

          // get item name and price
          (function(i, link) {
            $.ajax({
              url: "/ajax/item/",
              data: {link: link}
            }).done(function(data) {
              if ("error" in data) {
                $(".item[link='" + i + "'] .name").html(data["error"]["reason"] + " (" + data["error"]["details"] + ")");
              }
              else {
                var name = data["result"]["name"],
                    price = data["result"]["price"],
                    currency = data["result"]["currency"];

                $(".item[link='" + i + "'] .name").html("<a href='" + link + "' target='_blank'>" + name + "</a>");
                $(".item[link='" + i + "'] .price").html(price + " <small>" + currency + "</small>");
              }

              clearTimeout(enableTimeout); enableTimeout = setTimeout(function() {
                // re-enable submit button
                $("form.load-seller-rating button[type='submit']").prop('disabled', false);

                // allow from export to excel
                $("form.load-seller-rating a.export").show();
              }, 5000);
            });
          }(i, link));
        }
      }
    });
  });
});

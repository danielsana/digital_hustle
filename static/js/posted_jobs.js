function load_jobs(currentPage, job_title) {
  // alert("here")
  if (!currentPage) {
    currentPage = 1;
  }
  $.ajax({
    url: "/company/search",
    method: "POST",
    data: {
      currentPage: currentPage,
      job_title: job_title,
    },
    success: function (data) {
      $("#posted_jobs").html(data.htmlresponse);
      if (parseInt($("#currentPage").val(), 0) == 1) {
        $("#prev").prop("disabled", true);
        $("#prev").css({ "background-color": "#ddd", color: "black" });
      }

      if (
        parseInt($("#currentPage").val(), 0) == parseInt($("#total").val(), 0)
      ) {
        $("#next").prop("disabled", true);
        $("#next").css({ "background-color": "#ddd", color: "black" });
      }
    },
  });
}
function fetch_jobs() {
  var job_title = $("#search_posted_job").val();
  var currentPage = 1;
  // alert("job_type")
  load_jobs(currentPage, job_title);
}
$("#search_posted_job").keyup(function () {
  fetch_jobs();
  // alert("job_type")
});

$(document).ready(function () {
  // load jobs
  load_jobs();
});

function prev_jobs() {
  var job_title = $("#search_posted_job").val();
  var currentPage = parseInt($("#currentPage").val(), 0);
  // if (currentPage > 1) {
  //     load_jobs(currentPage - 1);
  // }
  currentPage -= 1;
  load_jobs(currentPage, job_title);
}

function next_jobs() {
  var job_title = $("#search_posted_job").val();
  var currentPage = parseInt($("#currentPage").val(), 0);
  currentPage += 1;
  load_jobs(currentPage, job_title);
}
function pages_jobs(page_no) {
  var job_title = $("#search_posted_job").val();
  load_jobs(page_no, job_title);
}

function load_applicants(currentPage, professional_title,job_id) {

    //   alert("hi");
    if (!currentPage) {
      currentPage = 1;
    }
    if (!job_id) {
      job_id = $('#job_id').val();
    }
    

    $.ajax({
      url: "/company/search/applicants/"+job_id,
      method: "POST",
      data: {
        currentPage: currentPage,
        professional_title: professional_title
      },
      success: function (data) {
        //   console.log(data);
        $("#applicants").html(data.htmlresponse);
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
    var professional_title = $("#search_posted_job").val();
    var currentPage = 1;
    // alert("job_type")
    load_applicants(currentPage, professional_title);
  }
  $("#search_posted_job").keyup(function () {
    fetch_jobs();
    // alert("job_type")
  });
  
  $(document).ready(function () {
    // load jobs
    load_applicants();
    //   alert("here");    
  });
  
  function prev_jobs() {
    var professional_title = $("#search_posted_job").val();
    var currentPage = parseInt($("#currentPage").val(), 0);
    // if (currentPage > 1) {
    //     load_applications(currentPage - 1);
    // }
    currentPage -= 1;
    load_applicants(currentPage, professional_title);
  }
  
  function next_jobs() {
    var professional_title = $("#search_posted_job").val();
    var currentPage = parseInt($("#currentPage").val(), 0);
    currentPage += 1;
    load_applicants(currentPage, professional_title);
  }
  function pages_jobs(page_no) {
    var professional_title = $("#search_posted_job").val();
    load_applicants(page_no, professional_title);
  }
  
// function load_work_experience(currentPage = 1, itemsPerPage = 5) {
//     $.ajax({
//         url: "/candidate/get-work-experience",
//         method: "POST",
//         data: {
//             currentPage: currentPage,
//             itemsPerPage: itemsPerPage,
//         },
//         success: function (data) {
//             if (data.error) {
//                 console.error(data.error);
//                 return;
//             }

//             $("#work-experience-table-body").html(data.htmlresponse);
//             $("#currentPage").val(data.currentPage);
//             $("#total").val(data.total);

//             let totalPages = Math.ceil(data.total / itemsPerPage);

//             $("#current-page-display").text(data.currentPage);
//             $("#total-pages-display").text(totalPages);

//             $("#prev").prop("disabled", data.currentPage == 1);
//             $("#next").prop("disabled", data.currentPage == totalPages);
//         },
//     });
// }

// $(document).ready(function() {
//     // Initialize the hidden inputs
//     $('body').append('<input type="hidden" id="currentPage" value="1">');
//     $('body').append('<input type="hidden" id="total" value="1">');

//     load_work_experience();

//     $("#prev").on("click", function() {
//         let currentPage = parseInt($("#currentPage").val(), 10);
//         if (currentPage > 1) {
//             load_work_experience(currentPage - 1);
//         }
//     });

//     $("#next").on("click", function() {
//         let currentPage = parseInt($("#currentPage").val(), 10);
//         let totalPages = Math.ceil(parseInt($("#total").val(), 10) / 5);
//         if (currentPage < totalPages) {
//             load_work_experience(currentPage + 1);
//         }
//     });
// });


function loadWorkExperience(currentPage = 1, itemsPerPage = 5) {
    $.ajax({
        url: "/candidate/get-work-experience",
        method: "POST",
        data: {
            currentPage: currentPage,
            itemsPerPage: itemsPerPage,
        },
        success: function (data) {
            if (data.error) {
                console.error(data.error);
                return;
            }

            $("#work-experience-table-body").html(data.htmlresponse);
            $("#currentPageWorkExperience").val(data.currentPage);
            $("#totalWorkExperience").val(data.total);

            let totalPages = Math.ceil(data.total / itemsPerPage);

            $("#current-page-display-work-experience").text(data.currentPage);
            $("#total-pages-display-work-experience").text(totalPages);

            $("#prev-work-experience").prop("disabled", data.currentPage == 1);
            $("#next-work-experience").prop("disabled", data.currentPage == totalPages);
        },
    });
}

$(document).ready(function() {
    // Initialize hidden inputs
    $('body').append('<input type="hidden" id="currentPageWorkExperience" value="1">');
    $('body').append('<input type="hidden" id="totalWorkExperience" value="1">');

    loadWorkExperience();

    $("#prev-work-experience").on("click", function() {
        let currentPage = parseInt($("#currentPageWorkExperience").val(), 10);
        if (currentPage > 1) {
            loadWorkExperience(currentPage - 1);
        }
    });

    $("#next-work-experience").on("click", function() {
        let currentPage = parseInt($("#currentPageWorkExperience").val(), 10);
        let totalPages = Math.ceil(parseInt($("#totalWorkExperience").val(), 10) / 5);
        if (currentPage < totalPages) {
            loadWorkExperience(currentPage + 1);
        }
    });
});


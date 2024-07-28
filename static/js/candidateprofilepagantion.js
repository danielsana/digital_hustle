function loadCertifications(currentPage = 1, itemsPerPage = 5) {
    $.ajax({
        url: "/candidate/get-certifications",
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

            $("#certifications-table-body").html(data.htmlresponse);
            $("#currentPageCertifications").val(data.currentPage);
            $("#totalCertifications").val(data.total);

            let totalPages = Math.ceil(data.total / itemsPerPage);

            $("#current-page-display-certifications").text(data.currentPage);
            $("#total-pages-display-certifications").text(totalPages);

            $("#prev-certifications").prop("disabled", data.currentPage == 1);
            $("#next-certifications").prop("disabled", data.currentPage == totalPages);
        },
    });
}

$(document).ready(function() {
    // Initialize hidden inputs
    $('body').append('<input type="hidden" id="currentPageCertifications" value="1">');
    $('body').append('<input type="hidden" id="totalCertifications" value="1">');

    loadCertifications();

    $("#prev-certifications").on("click", function() {
        let currentPage = parseInt($("#currentPageCertifications").val(), 10);
        if (currentPage > 1) {
            loadCertifications(currentPage - 1);
        }
    });

    $("#next-certifications").on("click", function() {
        let currentPage = parseInt($("#currentPageCertifications").val(), 10);
        let totalPages = Math.ceil(parseInt($("#totalCertifications").val(), 10) / 5);
        if (currentPage < totalPages) {
            loadCertifications(currentPage + 1);
        }
    });
});

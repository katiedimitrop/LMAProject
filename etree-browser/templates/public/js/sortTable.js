function sortTable() {
$('#dtOrderExample').DataTable({
"order": [[ 5, "asc" ]]
});
$('.dataTables_length').addClass('bs-select');
}
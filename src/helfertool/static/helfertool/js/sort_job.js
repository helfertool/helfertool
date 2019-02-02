function handle_sort_up(item_num_cur)
{
    _handle_sort(item_num_cur, -1)
}

function handle_sort_down(item_num_cur)
{
    _handle_sort(item_num_cur, +1)
}

function _handle_sort(item_num_cur, direction)
{
    var item_num_swap = item_num_cur + direction;

    if(_item_exists(item_num_cur) && _item_exists(item_num_swap))
    {
        // get name, pk and order
        data_cur = _get_data(item_num_cur);
        data_swap = _get_data(item_num_swap);

        // move item in list
        _set_item(item_num_cur, data_swap[0], data_swap[1]);
        _set_item(item_num_swap, data_cur[0], data_cur[1]);

        // change order in input fields
        _set_order(data_cur[1], data_swap[2]);
        _set_order(data_swap[1], data_cur[2]);
    }
}

function _item_exists(item_num)
{
    return $("#item_" + item_num).length == 1;
}

// return name, pk and order
function _get_data(item_num)
{
    var item = $("#item_" + item_num)[0];

    var name = item.innerText;
    var pk = item.dataset.pk;

    var order = $("input[name='order_job_"+pk+"']")[0].value;

    return [name, pk, order];
}

function _set_item(item_num, name, pk)
{
    var item = $("#item_" + item_num)[0];

    item.innerText = name
    item.dataset.pk = pk;

}

function _set_order(pk, order)
{
    $("input[name='order_job_"+pk+"']")[0].value = order;
}

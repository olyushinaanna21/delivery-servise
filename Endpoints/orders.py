from fastapi import APIRouter, HTTPException
from Models.order import OrdersPostRequest, AssignOrdersRequest, CompleteOrderRequest
from Endpoints.couriers import couriers_db
from Fuctions.helpFunc import get_available_orders, get_courier_assigned_orders, filter_compatible_orders, get_current_time_iso

#создаем роутер для заказов
router = APIRouter(prefix="/orders", tags=["Заказы"])

orders_db = {}


#создание заказа
@router.post("", status_code=201)
def create_orders(request: OrdersPostRequest):
    successful = []#успешные заказы
    failed = []#ошибочные заказы
    seen_ids = set() #проверка id на дубликаты

    for order in request.data:

        #дубликат внутри айди запроса
        if order.order_id in seen_ids:
            failed.append({"id": order.order_id})
            continue

        #заказ с таким айди существует в бд
        if order.order_id in orders_db:
            failed.append({"id": order.order_id})
            continue

        #если все нормально, то сохраняем заказ
        seen_ids.add(order.order_id)

        orders_db[order.order_id] = {
            "order_id": order.order_id,
            "weight": order.weight,
            "region": order.region,
            "delivery_hours": order.delivery_hours,
            "status": "available",
            "assigned_courier_id": None,
            "assign_time": None,
            "complete_time": None
        }
        successful.append({"id": order.order_id})

    #при ошибках 400 + список проблемных айди
    if failed:
        raise HTTPException(
            status_code=400,
            detail={
                "validation_error": {
                    "orders": failed
                }
            }
        )

    #успех 201 + успешные заказы
    return {"orders": successful}




#назначение максимального кол-ва заказов
@router.post("/assign")
def assign_orders(request: AssignOrdersRequest):
    #существование курьера
    if request.courier_id not in couriers_db:
        raise HTTPException(
            status_code=400,
            detail=f"Курьер с id {request.courier_id} не найден"
        )

    courier = couriers_db[request.courier_id]

    #получаем заказы которые уже есть у курьера
    assigned_orders = get_courier_assigned_orders(request.courier_id, orders_db)

    #если они есть возвращаем с временем назначения
    if assigned_orders:
        assign_time = assigned_orders[0].get("assign_time")
        return {
            "orders": [{"id": order["order_id"]} for order in assigned_orders],
            "assign_time": assign_time
        }

    #получаем доступные заказы(статус авелибл)
    available_orders = get_available_orders(orders_db)

    if not available_orders:
        return {"orders": []}  #если нет доступных заказов пустой список

    #проверяем что заказы подходят курьеру
    compatible_orders = filter_compatible_orders(available_orders, courier)

    if not compatible_orders:
        return {"orders": []}  #если нет подходящих заказов пустой список

    #сортировка заказов по весу сначала легкие, чтобы вместить больше, району и тд тк по тз надо максимальное кол-во
    compatible_orders.sort(key=lambda x: x["weight"])

    #назначаем заказы
    assign_time = get_current_time_iso()
    assigned_order_ids = []


    #проверка не превысили ли грузоподьемность(уже проверяли ,но на всякий случай)
    for order in compatible_orders:
        total_weight = sum(o.get("weight", 0) for o in assigned_order_ids) + order["weight"]
        if total_weight > courier["max_load"]:
            continue

        #назначили заказ
        order["status"] = "assigned"
        order["assigned_courier_id"] = request.courier_id
        order["assign_time"] = assign_time
        assigned_order_ids.append(order)


    if assigned_order_ids:
        return {
            "orders": [{"id": order["order_id"]} for order in assigned_order_ids],
            "assign_time": assign_time
        }
    else:
        return {"orders": []}





#завершение заказа
@router.post("/complete")
def complete_order(request: CompleteOrderRequest):
    #существует ли заказ по айди
    if request.order_id not in orders_db:
        raise HTTPException(
            status_code=400,
            detail=f"Заказ с id {request.order_id} не найден"
        )

    order = orders_db[request.order_id]

    #заказ уже завершен или нет
    if order.get("status") == "completed":
        return {"order_id": request.order_id}

    #заказ должен быть назначен
    if order.get("status") != "assigned":
        raise HTTPException(
            status_code=400,
            detail=f"Заказ {request.order_id} не назначен)"
        )

    #заказ назначен именно этому курьеру
    if order.get("assigned_courier_id") != request.courier_id:
        raise HTTPException(
            status_code=400,
            detail=f"Заказ {request.order_id} назначен другому курьеру"
        )

    #если все нормально , то завершаем заказ
    order["status"] = "completed"
    order["complete_time"] = request.complete_time

    return {"order_id": request.order_id}
# Do not modify these lines
__winc_id__ = "d7b474e9b3a54d23bca54879a4f1855b"
__human_name__ = "Betsy Webshop"

import populate_betsy_db
populate_betsy_db.populate_betsy()

# Add your code after this line
import models_betsy
import enchant
M = models_betsy


def search(term):
    # correct possible spelling errors in input
    dict = enchant.Dict("en_US")
    if dict.check(term) == False:
        suggestions = dict.suggest(term)
        if suggestions:
            print('Was your spelling correct?')
            term_old = term
            term = suggestions[0]
            print('We used "' + term + '" instead of "' + term_old + '"'  )

    query_search = (M.Product.select().where(M.Product.name.contains(term)|M.Product.description.contains(term)))
    print('---SEARCH RESULT---')
    print('prod.name, prod.description, prod.price_per_unit, prod.stock, prod.owner')
    for prod in query_search:
        print(prod.name, prod.description, prod.price_per_unit, prod.stock, prod.owner)
   

def list_user_products(user_id):
    
    query_user_products = (M.Product.select(M.Product, M.User)
                        .join(M.User)
                        .where(M.User.id == user_id))
    print('--- PRODUCTS of User' + str(user_id) + '---')
    print('prod.owner.name, prod.name, prod.description, prod.price_per_unit, prod.stock')
    for prod in query_user_products:
            print(prod.owner.name, prod.name, prod.description, prod.price_per_unit, prod.stock)


def list_products_per_tag(tag_id):
    query = (M.ProductTag
             .select(M.ProductTag,M.Product,M.Tag)
            .join(M.Product)
            .switch(M.ProductTag)
            .join(M.Tag)
            .where(M.Tag.id==tag_id))
    print('--- PRODUCTS with tag' + str(tag_id) + '---')
    print('prodtag.product.name, prodtag.tag.name')
    for prodtag in query:
        print(prodtag.product.name, prodtag.tag.name)


def add_product_to_catalog(user_id, product):
    models_betsy.Product.create(name=product, description='Product_DescriptionX', price_per_unit=100, stock=100, owner=user_id,tag=1) 
    

def update_stock(product_id, new_quantity):
    product = M.Product.select().where(M.Product.id == product_id).first()
    product.stock = new_quantity
    product.save()


def purchase_product(product_id, buyer_id, quantity):
    M.Transaction.create(buyer=buyer_id, product=product_id, quantity=quantity) 


def remove_product(product_id):
    product = M.Product.get(M.Product.id == product_id)
    product.delete_instance()


def handle_purchase(seller_id,product_id,buy_quantity):
    product = (M.Product
            .select(M.Product, M.User)
            .join(M.User)
            .where((M.Product.id == product_id) & (M.User.id == seller_id))
            .first())

    if product is None:
        producttemp = M.Product.get(M.Product.id == product_id)
        usertemp    = M.User.get(M.User.id == seller_id)
        print('Selected product (', producttemp.name, ')is not owned by selected seller(', usertemp.name, ')')
    elif product.stock < buy_quantity:
        print('Product stock is to low: ', product.stock, '(', buy_quantity , ' was requested)')
    else:
        purchase_product(product.id, seller_id, buy_quantity)
        updated_stock = product.stock - buy_quantity
        update_stock(product.id, updated_stock)
             
        if product.stock == buy_quantity:
            producttemp = M.Product.get(M.Product.id == product_id)
            usertemp    = M.User.get(M.User.id == seller_id)
            remove_product(product_id)
            print(producttemp.name + ' of ' + usertemp.name + ' removed')


## TESTING THE FUNCTIONS
if __name__ == "__main__":
    print('#1a. ############## search(term) ################')
    search('sweater')
    print('#1a. ############## search(term) wrong spelling ################')
    search('sweahter')
    
    print('#2.############## list_user_products(user_id) ################')
    list_user_products(user_id=1)
    list_user_products(user_id=2)
 
    print('#3.############## list_products_per_tag(tag_id) ################')
    list_products_per_tag(tag_id=4)
   
    print('#4.############## add_product_to_catalog(user_id, product) ################')
    add_product_to_catalog(user_id=5, product='Product_nameX')
    print('---- Test if product was added: M.print_all_procucts()')
    M.print_all_products()  

    print('#5.############## update_stock(product_id, new_quantity) ################')
    update_stock(product_id=1, new_quantity=600)
    print('---- Test if stock was updated: M.print_all_procucts()')
    M.print_all_products()  

    print('#6.############## purchase_product(product_id, buyer_id, quantity) ################')
    purchase_product(product_id=1, buyer_id=1, quantity=5)
    print('---- Test if tranaction was added:')
    print('mod.buyer.name, mod.product.name, mod.quantity')
    query_all = M.Transaction.select()
    for mod in query_all:
        print(mod.buyer.name, mod.product.name, mod.quantity)

    print('#7.############## remove_product(product_id) ################')
    remove_product(product_id=7)
    print('---- Test if product 7 was removed:')
    M.print_all_products()  

    print('#8. ############## Handle a purchase between a buyer and a seller for a given product')
    handle_purchase(seller_id=5,product_id=5,buy_quantity=40)
    print('---- Test if quantity of product 5 is now 10:')
    M.print_all_products()  
## A very first documentation of DB-NEF package.

1. Configuration
change 
`engine = create_engine('postgresql://postgres:postgres@localhost/test_database3', echo = True)`
in `config.py` to match the database configuration of local postgresql. 

2. Creations of a Table class and its corresponding Table from a given class

Note, all class names fit Camel rule, and table names fit snake rule. E.g.,

- class name = `AClass`
- its table class name = `AClassTable`
- its table name = `a_class`

It is needed to be mentioned is, this dynamic table creation can only deal with a class with 
`field()` method in python < 3.7, which would return its field attributes. For example, 

```python
import dbnef as db
import srfnef as nef 
import numpy as np

@nef.typing.dataclass
class BankAccount:
    data: np.ndarray
    val: int
    
@nef.typing.dataclass
class Person:
    name: str
    val: int
    bank_account: BankAccount
    

BankAccount.fields()
>>> {'val': Attribute(name='val', default=NOTHING, validator=None, repr=True,
 cmp=True, hash=None, init=True, metadata=mappingproxy({}), type=<class 'int'>, 
 converter=None, kw_only=False)}

```

After declared a class (e.g., `Person`), we can create a table class by
```python
table_class = db.create_table_class(Person)
```

or create a table by 
```python
table_class = db.create_table(Person)
```

when creating a table, its table class will be created automatically. 

3. add an object into table, with labeled pre-filled. 
An object can be filled into its corresponding table by 
```python
account1 = BankAccount(np.zeros(100), 100)
account2 = BankAccount(np.zeros(200), 200)
account3 = BankAccount(np.zeros(100), 100)
person1 = Person('123', 1, None)
person2 = Person('231', 2, account2)
person3 = Person('312', 3, account3)
db.add_object_to_table(person1)
db.add_object_to_table(person2)
db.add_object_to_table(person3)
```
The `data` field data would be automatically saved to resource table to fit the following 
database layers. 

4. HASH check
If a resource or object has been in dataset, it will not be added again.
 
For example, with a database tho have been added with the `account` and `person`s above, we cannot 
add another `person1`.

```python
db.add_object_to_table(person1)
>>> Warning: the inserting object has already been inserted. locate at person/id=1
>>> (<dbnef.create_table_class.PersonTable at 0x7faf0674d9e8>,
 '52a6eb687cd22e80d3342eac6fcc7f2e19209e8f83eb9b82e81c6f3e6f30743b')
```

5. Query an object with its table name and id
The default query method of an object in table is with its id. For example, 
```python
objs = db.query_object_with_id(Person, ids = [1, 2])
objs
>>> [Person(name='123', val=1, bank_account=None),
 Person(name='231', val=2, bank_account=BankAccount(val=200))]

```


6. Filters
if you want to get some objects with filters on some column in table, you need to 
```python
table_class = db.create_table_class(Person)
ids = db.query_id_with_filter(table_class, filters = [table_class.name == '231', table_class.id > 6, table_class.val == 2])
print(ids)
objs = db.query_object_with_id(Person, ids = ids)
print(objs)
>>> [8]
>>> Person(name='231', val=2, bank_account=BankAccount(val=200))
```

Note, the argument of filter function `db.query_id_with_filter` is table class. And it will 
return ids. 
This ids can be used to query its corresponding objects. 

7. Filters on labels. 
When filtering labels, the mechanic is kindly different. Usually, you want to find some rows in 
table which have the labels you desired. However, the sqlalchemy doesn't support such kind of 
filtering. So we have another filtering function, namely `query_id_with_filter_and_labels`

```python
ids2 = db.query_id_with_filter_and_labels(table_class, filters=[], label_filters=['temp1'])
```


8. Updating labels and clear labels
If you want to update the lables in some rows in a table, you need to do 
```python
db.update_labels('person', ids = [5, 8], labels=['temp1'], mode = 'new')
```
or 
```python
db.update_labels('person', ids = [5, 8], labels=['temp1'], mode = 'add')
```
which would create / append labels on the label cell in these rows. 

Another useful function is 
`clear_labels`
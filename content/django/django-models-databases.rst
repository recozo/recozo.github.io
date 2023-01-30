模型与数据库
######################################################################

:date: 2023-01-19 10:20
:modified: 2023-01-30 18:40
:slug: django-models-and-databases
:tags: django, models and databases

1. 利用模型执行数据库操作
======================================================================

一旦创建数据模型后，Django 自动生成一套数据库操作 API，可以执行创建、检索、更新
和删除操作。

为了用 Python 对象展示数据表对象，Django 使用了一套直观的系统：一个模型类代表的是
数据库表，一个模型类的实例代表的是数据库表中的一条记录。

字段查询，即如何制定 SQL WHERE 子句，以关键字参数的形式传递给 QuerySet 方法 
filter()、exclude() 和 get()。
基本的查询关键字参数遵照 field__lookuptype=value，查询类型有二十多种。
详细资料：
https://docs.djangoproject.com/en/4.1/ref/models/querysets/#field-lookups

跨关系查询，Django 提供了一种强大而直观的方式来“追踪”查询中的关系，在后台自动为你处理
SQL JOIN。要跨一个关系，使用跨模型的相关字段的字段名，用双下划线分割，（根据实际需要，
跨度不受限）直到得到你想要的字段，如
Blog.objects.filter(entry__authors__name='Lennon')，就有二个跨度。
它也可以反向工作，默认情况下，你在查找中使用模型的小写名称来引用一个 “反向” 关系。
也可以不使用小写名称，通过使用 ForeignKey.related_query_name 自定义目标模型中
反向过滤器的名称。如果设置了，它默认为 related_name 或 default_related_name 的值，
否则默认为模型的小写名称。

2. 关联对象
======================================================================

正向访问：当你在模型中定义了关联关系（如 ForeignKey， OneToOneField， 或
ManyToManyField），该模型的实例将会自动获取一套 API，能快捷地访问关联对象。

逆向访问：Django也提供了从关联关系的另一边进行访问的API，即从被关联模型到
定义该关联关系的模型的访问。例如，一个Blog对象b能通过entry_set属性b.entry_set.all()
访问包含所有关联Entry对象的列表。

#.  一对多关联
  
    正向访问：If a model has a ForeignKey, instances of that model will have 
    access to the related (foreign) object via the foreign-key attribute.

    逆向访问：If a model(source) has a ForeignKey, instances of the foreign-key
    model(target) will have access to a Manager that returns all instances of
    the source model. By default, this Manager is named FOO_set, where FOO is
    the source model name, lowercased. You can override the FOO_set name by
    setting the related_name parameter in the ForeignKey definition.

#.  多对多关联

    多对多关联的两端均自动获取访问另一端的 API。该 API 的工作方式类似一对多关联的逆向访问。

    定义了 ManyToManyField 的模型使用字段名作为属性名，而 “反向” 模型使用源模型名的
    小写形式，加上 '_set' （就像反向一对多关联一样）。
    和 ForeignKey 一样， ManyToManyField 也能指定 related_name。

#.  一对一关联

    若在模型中定义了 OneToOneField，该模型的实例只需通过该属性就能访问关联对象。
    不同点在于 “反向” 查询。一对一关联所关联的对象也能访问 Manager 对象，
    但这个 Manager 仅代表一个对象，而不是对象的集合。

#.  逆向关联是如何实现的

    其它对象关联映射实现要求你在两边都定义关联关系。而 Django 开发者坚信这违反了
    DRY 原则（不要自我重复），故 Django 仅要求你在一端定义关联关系。

    但这是如何实现的呢，给你一个模型类，模型类并不知道是否有其它模型类关联它，
    直到其它模型类被加载？
    
    答案位于应用注册。 Django 启动时，它会导入 INSTALLED_APPS 列出的每个应用，
    和每个应用中的 model 模块。无论何时创建了一个新模型类，Django 为每个关联模型
    添加反向关联。若被关联的模型未被导入，Django 会持续追踪这些关联，并在关联模型
    被导入时添加关联关系。
    
    出于这个原因，包含你所使用的所有模型的应用必须列在 INSTALLED_APPS 中。否则，
    反向关联可能不会正常工作。

3. 为模型提供初始数据
======================================================================

第一次设置应用程序时，有时需要用硬编码的数据预填充数据库。你可以通过数据迁移
（data migration）或固定数据（fixture）提供初始数据。

#.  使用数据迁移

    https://docs.djangoproject.com/en/4.1/topics/migrations/#data-migrations

#.  使用固定数据

    https://docs.djangoproject.com/en/4.1/howto/initial-data/

    固定数据是 Django 知道如何导入数据库的数据集合。若你已有一些可用数据，
    创建固定数据最直接的方式是使用 manage.py dumpdata 命令。当然，你也可以手写固定数据；
    固定数据支持 JSON，XML 或 YAML （要求已安装 PyYAML）格式。

    .. code-block:: bash

       $ ./manage.py dumpdata -h
       $ ./manage.py dumpdata myapp --format json --indent 2 --output mydump

    你使用 manage.py loaddata 命令导入固定数据，Django 会在三个位置搜索固定数据：

    #.  在每个安装的应用程序的 fixtures 目录中
    #.  在 FIXTURE_DIRS 配置中指定的任何目录中
    #.  固定数据中包括的目录路径

    .. code-block:: bash

       $ ./manage.py loaddata -h
       $ ./manage.py loaddata foo/bar/mydata
       $ ./manage.py loaddata foo/bar/mydata.json

    如果没有指定文件的扩展名，会探索所有可用的固定数据内容，如果指定了文件扩展名，
    则只有该类型的固定数据才会被加载。

    以上最后一条命令，将对每个安装的应用程序搜索 <app_label>/fixtures/foo/bar/mydata.json，
    为 FIXTURE_DIRS 中的每个目录搜索 <dirname>/foo/bar/mydata.json，
    并搜索字面路径 foo/bar/mydata.json。
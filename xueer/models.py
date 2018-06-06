# coding:utf-8
"""
    models.py
    `````````

    : SQL数据库模块
    : -- Permission             权限
    : -- AnonymousUser          匿名用户
    : -- Comments               评论
    : -- CourseCategories       课程主分类
    : -- CourseTag              课程标签中间表
    : -- CourseTypes            学分类别
    : -- Courses                课程
    : -- CoursesSubCategories   课程二级分类
    : -- Role                   用户角色
    : -- Tags                   标签
    : -- Teachers               老师类
    : -- Tips                   运营文章
    : -- User                   用户
    : -- CourseQuestion         提问
    ：-- Answer                　回答

    : copyright: (c) 2016 by MuxiStudio
    : license: MIT
"""

from datetime import datetime
from flask_login import UserMixin, AnonymousUserMixin
from . import login_manager, db
from flask import current_app, url_for, request,abort
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeSerializer as Serializer
from .exceptions import ValidationError
import base64
import requests
import os


class Permission:
    """
    Permission 权限

    1. COMMENT: 0x01
    2. MODERATE_COMMENTS: 0x02
    3. ADMINISTER: 0x04
    """
    COMMENT = 0x01
    MODERATE_COMMENTS = 0x02
    ADMINISTER = 0x04


class Role(db.Model):
    """
    Role: 用户角色

    1. User: COMMENT
    2. Moderator: MODERATE_COMMENTS
    3. Administrator: ADMINISTER

    :func insert_roles: 创建用户角色, 默认是普通用户
    """
    __table_args__ = {'mysql_charset': 'utf8'}
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role',
                            lazy='dynamic', cascade='all')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.COMMENT, True),
            'Moderator': (Permission.COMMENT |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (
                Permission.COMMENT |
                Permission.MODERATE_COMMENTS |
                Permission.ADMINISTER,
                False
            )
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


# a secondary table
# 多对多关系的中间表
UCLike = db.Table(
    'user_like',
    db.Column('user_id', db.Integer,
              db.ForeignKey('users.id', ondelete="CASCADE")),
    db.Column('course_id', db.Integer,
              db.ForeignKey('courses.id', ondelete="CASCADE"))
)

UCMLike = db.Table(
    'user_comment_like',
    db.Column('user_id', db.Integer,
              db.ForeignKey('users.id', ondelete="CASCADE")),
    db.Column('comment_id', db.Integer,
              db.ForeignKey('comments.id', ondelete="CASCADE"))
)


UTLike = db.Table(
    'user_tips_like',
    db.Column('user_id', db.Integer,
              db.ForeignKey('users.id', ondelete="CASCADE")),
    db.Column('tips_id', db.Integer,
              db.ForeignKey('tips.id', ondelete="CASCADE"))
)



class CourseTag(db.Model):
    """
    CourseTag: 课程标签中间表

    (course_id, tag_id) 二元组作为主键
    :var course_id: 指向课程的外键(多对多关系), CASCADE: 级联
    :var tag_id: 指向标签的外键, CASCADE: 级联
    :var count: 纪录(课程, 标签)的引用次数, 作为热门标签的统计
    """
    __table_args__ = {'mysql_charset': 'utf8'}
    __tablename__ = 'courses_tags'
    course_id = db.Column(db.Integer,
                          db.ForeignKey('courses.id', ondelete="CASCADE"),
                          primary_key=True)
    tag_id = db.Column(db.Integer,
                       db.ForeignKey('tags.id', ondelete="CASCADE"),
                       primary_key=True)
    count = db.Column(db.Integer, default=0)



class User(UserMixin, db.Model):
    """
    User: 用户

    :var id: 主键
    :var username: 用户名
    :var role_id: 外键, 与用户角色的一对多关系
    :var email: 邮箱
    :var qq: qq
    :var major: 专业
    :var password_hash: 密码的hash值, 单向加密
    :var comments: 关系, 多对一, 用户发表的评论
    :var phone: 电话
    :var school: 学院
    : var recommend_count：当前用户推荐来的用户的数量

    :property password: 不允许读取用户密码明文
    :property password set: 设置用户密码, 单向加密hash值

    :func verify_password: 根据密码明文验证密码, 实际比对hash值
    :func generate_auth_token: 结合密钥, 根据用户的id生成token, 用于HTTP Basic验证
    :func verify_auth_token: 结合密钥, 根据用户的token解析用户,进行相关操作
    :func can: 权限判断
    :func is_administrator: 管理员判断
    :func to_json: API json数据显示
    :func to_json2: API json数据显示
    :func from_json: API 读取json数据
    """
    __table_args__ = {'mysql_charset': 'utf8'}
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(164), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    email = db.Column(db.String(164), index=True, unique=True)
    qq = db.Column(db.String(164), index=True)
    major = db.Column(db.String(200), index=True)
    password_hash = db.Column(db.String(128))
    # confirmed = db.Column(db.Boolean,default=False)
    comments = db.relationship("Comments", backref='users',
                               lazy="dynamic", cascade='all')
    questions = db.relationship("CourseQuestion", backref='user',
                                lazy="dynamic", cascade='all')
    answers = db.relationship("Answer", backref='user',
                              lazy="dynamic", cascade='all')
    phone = db.Column(db.String(200), default=None)
    school = db.Column(db.String(200), index=True, default=None)
    avatar = db.Column(db.String(200))
    recommend_count=db.Column(db.Integer,default=0)



    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        import random
        import forgery_py

        random.seed()
        for i in range(count):
            u = User(username=forgery_py.name.full_name(),
                     role_id=random.choice([1, 2, 3]),
                     email=forgery_py.internet.email_address(),
                     qq=forgery_py.address.street_number() + forgery_py.address.street_number(),
                     major=forgery_py.name.job_title() + "_major",
                     password=base64.b64encode(forgery_py.lorem_ipsum.word()),
                     phone=forgery_py.address.phone(),
                     school=forgery_py.name.company_name() + "_school",
                     avatar=forgery_py.name.full_name() + "_avatar")
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        # 这里是要求前端将用户的密码进行base64编码
        password_decode = base64.b64decode(password)
        self.password_hash = generate_password_hash(password_decode)

    def verify_password(self, password):
        # password = base64.b64decode(password)
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self):
        """generate a token"""
        s = Serializer(
            current_app.config['SECRET_KEY']
            # expiration
        )
        return s.dumps({'id': self.id})

    def generate_private_promotion_link(self):
        import json
        X_API_Key = os.getenv("X_API_KEY")
        if not X_API_Key:
            print("请设置X_API_KEY环境变量")
            abort(500)
        headers = {'X-API-Key': X_API_Key}
        r = requests.post("https://kutt.it/api/url/submit", headers=headers,data={"target": "https://xueer.muxixyz.com/promotion/register/?id="+str(self.id)})
        return json.loads(r.content).get("shortUrl")

    @staticmethod
    def verify_auth_token(token):
        """verify the user with token"""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        # get id
        return User.query.get_or_404(data['id'])

    def can(self, permissions):
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        # is administrator
        return (self.role_id == 2)

    def to_json(self):
        json_user = {
            'id': self.id,
            'url': url_for('api.get_user_id', id=self.id, _external=True),
            'username': self.username,
            'email': self.email,
            'qq': self.qq,
            'major': self.major,
            'phone': self.phone,
            'school': self.school,
            "recommand_count": self.recommend_count
        }
        return json_user

    def to_json2(self):
        json_user = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'recommand_count': self.recommend_count
        }
        return json_user

    @staticmethod
    def from_json(json_user):
        username = json_user.get('username')
        password = json_user.get('password')
        email = json_user.get('email')
        role_id = json_user.get('roleid')
        qq = json_user.get('qq')
        major = json_user.get('major')
        phone = json_user.get('phone')
        school = json_user.get('school')
        recommend_id=json_user.get("recommender_id")
        if recommend_id is not None:
            recommender=User.query.get_or_404(int(recommend_id))
            recommender.recommend_count+=1
            db.session.add(recommender)
            db.session.commit()

        if username is None or username == '':
            raise ValidationError('用户名不能为空哦！')
        if password is None or password == '':
            raise ValidationError('请输入密码！')
        if email is None or email == '':
            raise ValidationError('请输入邮箱地址！')
        return User(username=username, password=password, email=email, role_id=role_id)

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):
    """
    AnonymousUser: 匿名用户

    :func can:
        权限判断, 匿名用户没有任何权限

    :func is_administrator:
        是否是管理员, 返回False

    :generate_auth_token:
        生成验证token, 匿名用户没有id, 不生成token
    """
    __table_args__ = {'mysql_charset': 'utf8'}

    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

    def generate_auth_token(self, expiration):
        return None


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Courses(db.Model):
    """
    Courses: 课程

    :var id: 主键
    :var name: 课程名
    :var category_id: 指向CourseCategory的外键, 课程主分类
    :var subcategory_id: 指向CoursesSubCategories的外键, 课程二级分类
    :var type_id: 指向CourseType的外键, 学分类别
    :var credit: 学分
    :var available: 课程是否可用
    :var score: 情感分析得分
    :var loctime: 上课地点和时间
    :var teacher: 老师姓名
    :var introduction: 课程介绍
    :var comment: 课程对应的评论关系: 一对多关系
    :var count: 课程对应的评论数
    :var likes: 课程对应的点赞数
    :var tags: 课程与标签的多对多关系, cascade级联删除
    :var users: 课程与用户点赞的多对多关系, cascade级联删除

    :property liked: 当前用户是否点赞了这门课
    :property hot_tags: 该课最热门(引用最多)的四个标签

    :func to_json: API json表示
    :func to_json2: API json表示
    :func from_json: API 读取json数据
    """
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(280))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    subcategory_id = db.Column(db.Integer, db.ForeignKey('subcategory.id'))
    type_id = db.Column(db.Integer, db.ForeignKey('type.id'))
    credit = db.Column(db.Integer)
    available = db.Column(db.Boolean)
    loctime = db.Column(db.Text)
    count = db.Column(db.Integer)
    score = db.Column(db.Integer)
    teacher = db.Column(db.String(164))
    introduction = db.Column(db.Text)
    comment = db.relationship('Comments', backref="courses",
                              lazy='dynamic', cascade='all')
    likes = db.Column(db.Integer, default=0)
    tags = db.relationship("CourseTag", backref="courses",
                           lazy="dynamic", cascade='all')
    users = db.relationship("User", secondary=UCLike,
                            backref=db.backref('courses', lazy="dynamic"),
                            lazy='dynamic', cascade='all')
    questions = db.relationship("CourseQuestion",
                                backref="course", lazy="dynamic", cascade='all')

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        import random
        import forgery_py

        random.seed()
        category_count = CourseCategories.query.count()
        subcategory_count = CoursesSubCategories.query.count()
        type_count = CourseTypes.query.count()
        for i in range(count):
            cg_id = CourseCategories.query.offset(random.randint(0, category_count - 1)).first().id
            sub_cg_id = CoursesSubCategories.query.offset(random.randint(0, subcategory_count - 1)).first().id
            tp_id = CourseTypes.query.offset(random.randint(0, type_count - 1)).first().id
            c = Courses(name=forgery_py.name.title() + "_CourseName",
                        category_id=cg_id,
                        subcategory_id=sub_cg_id,
                        type_id=tp_id,
                        credit=random.choice([1, 2, 3]),
                        available=random.choice([True, False]),
                        loctime=forgery_py.name.location() + "_loctime",
                        count=random.randrange(0, 100),
                        score=random.randrange(0, 10),
                        teacher=forgery_py.name.full_name(),
                        introduction=forgery_py.basic.text(),
                        )
            db.session.add(c)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    @property
    def average_usual_score(self):
        from sqlalchemy.sql import func
        average=Comments.query.with_entities(func.avg(Comments.usual_score)).\
            filter(Comments.course_id == self.id and Comments.usual_score is not None)
        return None if average[0][0] is None else int(average[0][0])

    @property
    def average_final_score(self):
        from sqlalchemy.sql import func
        average = Comments.query.with_entities(func.avg(Comments.final_score)). \
            filter(Comments.course_id == self.id and Comments.final_score is not None)
        return None if average[0][0] is None else int(average[0][0])


    @property
    def liked(self):
        token_headers = request.headers.get('authorization', None)
        if token_headers:
            token_8 = base64.b64decode(token_headers[6:])
            token = token_8[:-1]
            user = User.verify_auth_token(token)
            if user in self.users.all():
                return True
            else:
                return False
        else:
            return False

    @property
    def hot_tags(self):
        """
        返回热门的4个标签
        用空格隔开、组成4个字符串
        """
        # 查询记录
        s = ""
        ct = CourseTag.query.filter_by(course_id=self.id).all()
        sct = sorted(ct, lambda x, y: cmp(y.count, x.count))
        for link in sct[:4]:
            s = s + link.tags.name + " "
        return s[:-1]

    def to_json(self):
        if CourseTypes.query.filter_by(id=self.type_id).first() is None:
            credit_category = "无分类"
        else:
            credit_category = CourseTypes.query.filter_by(
                id=self.type_id).first().name
        if CoursesSubCategories.query.filter_by(
                id=self.subcategory_id).first() is None:
            sub_category = "无分类"
        else:
            sub_category = CoursesSubCategories.query.filter_by(
                id=self.subcategory_id).first().name

        json_courses = {
            'id': self.id,
            'title': self.name,
            'teacher': self.teacher,
            # 'comment_id': url_for('api.get_courses_id_comments',
            #                        id=self.id, _external=True),
            'comment_id': [i.id for i in self.comment],
            'hot_tags': self.hot_tags,
            'available': self.available,
            'score': self.score,
            'loctime': self.loctime,
            'likes': self.likes,  # 点赞的总数
            'like_url': url_for('api.new_courses_id_like',
                                id=self.id, _external=True),
            'liked': self.liked,  # 查询的用户是否点赞了
            'main_category': CourseCategories.query.filter_by(
                id=self.category_id).first().name,
            'sub_category': sub_category,
            'credit_category': credit_category,
            'views': self.count,  # 浏览量其实是评论数
            'average_final_score':self.average_final_score,
            'average_usual_score':self.average_usual_score
        }
        return json_courses

    def to_json2(self):
        if CourseTypes.query.filter_by(id=self.type_id).first() is None:
            credit_category = "无分类"
        else:
            credit_category = CourseTypes.query.filter_by(
                id=self.type_id).first().name
        if CoursesSubCategories.query.filter_by(
                id=self.subcategory_id).first() is None:
            sub_category = "无分类"
        else:
            sub_category = CoursesSubCategories.query.filter_by(
                id=self.subcategory_id).first().name
        json_courses2 = {
            'id': self.id,
            'title': self.name,
            'teacher': self.teacher,
            'available': self.available,
            'score': self.score,
            'loctime': self.loctime,
            'views': self.count,
            'likes': self.likes,
            'main_category': CourseCategories.query.filter_by(
                id=self.category_id).first().name,
            'sub_category': sub_category,
            'credit_category': credit_category,
            'average_final_score': self.average_final_score,
            'average_usual_score': self.average_usual_score
        }
        return json_courses2

    @staticmethod
    def from_json(json_courses):
        name = json_courses.get('name')
        teacher = json_courses.get('teacher')
        introduction = json_courses.get('introduction')
        category_id = json_courses.get('category_id')
        credit = json_courses.get('credit')
        # 二级课程分类和学分分类可选
        type_id = json_courses.get('type_id')
        subcategory_id = json_courses.get('sub_category_id')
        return Courses(
            name=name,
            teacher=teacher,
            category_id=category_id,
            type_id=type_id,
            subcategory_id=subcategory_id
        )

    def __repr__(self):
        return '<Courses %d>' % self.id


# CourseCategories
#   1     公共课
#   2     通识课
#   3     专业课
#   4     素质课
class CourseCategories(db.Model):
    __table_args__ = {'mysql_charset': 'utf8'}
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    courses = db.relationship("Courses", backref="category",
                              lazy="dynamic", cascade='all')
    subcategories = db.relationship("CoursesSubCategories",
                                    backref="category",
                                    lazy="dynamic",
                                    cascade='all')

    @staticmethod
    def generate_fake():
        from sqlalchemy.exc import IntegrityError
        course_categories = ["公共课", "通识课", "专业课", "素质课"]
        for i in course_categories:
            c_cg = CourseCategories(name=unicode(i))
            db.session.add(c_cg)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def __repr__(self):
        return '<CourseCategory %r>' % self.name


# CoursesSubCategories
# 1     通识核心课
# 2     通识选修课
class CoursesSubCategories(db.Model):
    __table_args__ = {'mysql_charset': 'utf8'}
    __tablename__ = 'subcategory'
    id = db.Column(db.Integer, primary_key=True)
    main_category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    name = db.Column(db.String(640))
    courses = db.relationship('Courses', backref='subcategory',
                              lazy='dynamic', cascade='all')

    @staticmethod
    def generate_fake():
        from sqlalchemy.exc import IntegrityError
        course_sub_categories = ["通识核心课", "通识选修课"]
        for i in course_sub_categories:
            c_sub_cg = CoursesSubCategories(name=unicode(i), main_category_id=2)
            db.session.add(c_sub_cg)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def __repr__(self):
        return "<SubCategory %r> % self.name"


# CourseTypes
#   id    name
#   1     理科
#   2     文科
#   3     艺体
#   4     工科
class CourseTypes(db.Model):
    __table_args__ = {'mysql_charset': 'utf8'}
    __tablename__ = 'type'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    courses = db.relationship("Courses", backref="type",
                              lazy="dynamic", cascade='all')

    @staticmethod
    def generate_fake():
        from sqlalchemy.exc import IntegrityError
        course_types = ["理科", "文科", "艺体", "工科"]
        for i in course_types:
            ct = CourseTypes(name=unicode(i))
            db.session.add(ct)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def __repr__(self):
        return '<CourseType %r>' % self.name


class Comments(db.Model):
    """
    Comments: 评论

    :var id: 主键, 唯一
    :var course_id: 指向课程的外键, 与课程的多对一关系
    :var user_id: 指向用户的外键, 与用户的多对一关系
    :var timestamp: 时间戳, 默认是系统时间(datetime.utcnow)
    :var body: 评论体(数据库直接存储html)
    :var likes: 点赞数
    :var is_useful:
    :var tip_id: 指向tip的外键, 与tip的多对一关系
    :var user: 与用户点赞的多对多关系

    :property time: 时间格式化
    :property liked: 当前用户是否点赞, 匿名用户默认返回False

    :func to_json: API json格式转换
    :func from_json: API json读取
    """
    __table_args__ = {'mysql_charset': 'utf8'}
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    usual_score=db.Column(db.Integer,nullable=True)
    final_score=db.Column(db.Integer,nullable=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    # user外键关联到user表的username
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    body = db.Column(db.Text)
    likes = db.Column(db.Integer, default=0)
    # is_useful计数
    is_useful = db.Column(db.Integer)
    tip_id = db.Column(db.Integer, db.ForeignKey('tips.id'))
    user = db.relationship(
        "User",
        secondary=UCMLike,
        backref=db.backref('comment', lazy="dynamic"),
        lazy='dynamic',
        cascade='all'
    )

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        import random
        import forgery_py

        random.seed()
        course_count = Courses.query.count()
        user_count = User.query.count()
        tip_count = Tips.query.count()
        for i in range(count):
            c_id = Courses.query.offset(random.randint(0, course_count - 1)).first().id
            user_id = User.query.offset(random.randint(0, user_count - 1)).first().id
            tip_id = Tips.query.offset(random.randint(0, tip_count - 1)).first().id
            cmt = Comments(
                course_id=c_id,
                user_id=user_id,
                timestamp=forgery_py.date.date(),
                body=forgery_py.basic.text(),
                likes=random.randrange(0, 100),
                is_useful=random.randrange(0, 20),
                tip_id=tip_id)
            db.session.add(cmt)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    @property
    def time(self):
        time_str = str(self.timestamp)
        time = time_str[0:10]
        return time

    @property
    def liked(self):
        token_headers = request.headers.get('authorization', None)
        if token_headers:
            token_8 = base64.b64decode(token_headers[6:])
            token = token_8[:-1]
            user = User.verify_auth_token(token)
            if user in self.user.all():
                return True
            else:
                return False
        else:
            return False

    def to_json(self):
        json_comments = {
            'id': self.id,
            'user_name': User.query.filter_by(
                id=self.user_id).first().username,
            'avatar': 'http://7xj431.com1.z0.glb.clouddn.com/1-140G2160520962.jpg',
            'date': self.time,
            'body': self.body,
            'usual_score':self.usual_score,
            'final_score':self.final_score,
            'is_useful': self.is_useful,
            'likes': self.likes,
            'liked': self.liked,
            'like_url': url_for('api.new_comments_id_like',
                                id=self.id, _external=True)
        }
        return json_comments

    @staticmethod
    def from_json(json_comments):
        body = json_comments.get('body')
        if json_comments.get("final_score") is not None:
            final_score=int(json_comments.get("final_score"))
        else:
            final_score=None
        if json_comments.get("usual_score") is not None:
            usual_score=int(json_comments.get("usual_score"))
        else:
            usual_score=None
        if body is None or body == '':
            raise ValidationError('评论不能为空哦！')
        return Comments(body=body,final_score=final_score,usual_score=usual_score)

    def __repr__(self):
        return '<Comments %r>' % self.id


class Teachers(db.Model):
    """
    Teachers 老师类: 目前没有使用
    """
    __tablename__ = 'teachers'
    __table_args__ = {'mysql_charset': 'utf8'}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    department = db.Column(db.String(150))
    introduction = db.Column(db.Text)
    phone = db.Column(db.String(20))
    weibo = db.Column(db.String(150))

    def to_json(self):
        json_teacher = {
            'id': self.id,
            'url': url_for('api.get_teacher_id', id=self.id, _external=True),
            'name': self.name,
            'department': self.department,
            'introduction': self.introduction,
            'phone': self.phone,
            'weibo': self.weibo,
            'courses': url_for('api.get_courses', teacher=self.id,
                               _external=True)
        }
        return json_teacher

    @staticmethod
    def from_json(request_json):
        name = request_json.get('name')
        department = request_json.get('department')
        introduction = request_json.get('introduction')
        phone = request_json.get('phone')
        weibo = request_json.get('weibo')
        return Teachers(
            name=name,
            department=department,
            introduction=introduction,
            phone=phone,
            weibo=weibo
        )

    def __repr__(self):
        return '<Teachers %r>' % self.name


class Tags(db.Model):
    """
    Tags: 标签

    :var id: 主键
    :var name: 标签名称
    :var count: 标签计数, 用于全站热门标签统计
    :var courses: 标签和课程的多对多关系

    :func to_json: API json数据
    :func from_json: API 读取json数据
    """
    __table_args__ = {'mysql_charset': 'utf8'}
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    count = db.Column(db.Integer, default=0)
    courses = db.relationship("CourseTag", backref="tags", lazy="dynamic",
                              cascade='all')

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        import random
        import forgery_py
        random.seed()
        for i in range(count):
            tg = Tags(name=forgery_py.lorem_ipsum.word(),
                      count=random.randrange(0, 200))
            db.session.add(tg)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def to_json(self):
        json_tag = {
            'id': self.id,
            'tag_url': url_for('api.get_tags_id', id=self.id, _external=True),
            'title': self.name
        }
        return json_tag

    @staticmethod
    def from_json(json_tag):
        name = json_tag.get('name')
        return Tags(name=name)

    def __repr__(self):
        return '<Tags %r>' % self.name


class Tips(db.Model):
    """
    Tips: 运营文章
    :var id: 主键
    :var title: 标题
    :var body: 运营文章(直接存储html)
    :var img_url: 文章对应的图片
    :var banner_url: 桌面版banner
    :var author: 运营妹子
    :var timestamp: 时间戳, 默认是系统时间
    :var likes: 文章对应的点赞数
    :var views: 文章的浏览量
    :var users: 文章和用户点赞的多对多关系

    :property time: 时间格式化
    :property liked: 用户是否点赞了这篇文章

    :func to_json: API json数据显示
    :func to_json2: API json数据显示
    :func from_json: API 读取json数据
    """
    __table_args__ = {'mysql_charset': 'utf8'}
    __tablename__ = 'tips'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    body = db.Column(db.Text)
    img_url = db.Column(db.Text)
    banner_url = db.Column(db.Text)
    author = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    # likes number
    likes = db.Column(db.Integer, default=0)
    # views counts
    views = db.Column(db.Integer, default=0)
    users = db.relationship(
        "User",
        secondary=UTLike,
        backref=db.backref('tips', lazy="dynamic"),
        lazy='dynamic', cascade='all'
    )
    comment = db.relationship('Comments', backref="tip",
                              lazy='dynamic', cascade='all')

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        import random
        import forgery_py
        random.seed()
        for i in range(count):
            tp = Tips(title=forgery_py.lorem_ipsum.title(),
                      body=forgery_py.basic.text(),
                      img_url=forgery_py.lorem_ipsum.sentence(),
                      banner_url=forgery_py.lorem_ipsum.sentence(),
                      author=forgery_py.name.full_name(),
                      timestamp=forgery_py.date.date(),
                      likes=random.randrange(0, 500),
                      views=random.randrange(0, 1000))
            db.session.add(tp)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    @property
    def time(self):
        time_str = str(self.timestamp)
        time = time_str[0:10]
        return time

    @property
    def liked(self):
        token_headers = request.headers.get('authorization', None)
        if token_headers:
            token_8 = base64.b64decode(token_headers[6:])
            token = token_8[:-1]
            user = User.verify_auth_token(token)
            if user in self.users.all():
                return True
            else:
                return False
        else:
            return False

    def to_json(self):
        json_tips = {
            'id': self.id,
            'title': self.title,
            'body': self.body,
            'url': url_for('api.get_tip_id', id=self.id, _external=True),
            'views': self.views,
            'likes': self.likes,
            'date': self.time,
            'img_url': self.img_url,
            'banner_url': self.banner_url,
            'liked':self.liked
        }
        return json_tips

    def to_json2(self):
        json_tips2 = {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'body': self.body,
            'likes': self.likes,
            'date': self.time,
            'banner_url': self.banner_url,
            'img_url': self.img_url,
            'liked':self.liked
        }
        return json_tips2

    @staticmethod
    def from_json(json_tips):
        title = json_tips.get('title')
        img_url = json_tips.get('img_url')
        body = json_tips.get('body')
        author = json_tips.get('author')
        banner = json_tips.get('banner_url')
        return Tips(
            title=title,
            body=body,
            img_url=img_url,
            author=author,
            banner_url=banner
        )

    def __repr__(self):
        return '<Tips %r>' % self.title


class CourseQuestion(db.Model):
    """
       CourseQuestion: 问大家对应的问题
       :var id: 主键
       :var content: 问题内容
       :var author_id: 作者id
       :var create_time: 提问时间
       :var course_id:　对应的课程id

       :func to_json
       """
    __table_args__ = {'mysql_charset': 'utf8'}
    __tablename__ = 'coursequestions'
    id = db.Column(db.Integer, primary_key=True)
    question_content = db.Column(db.String(200))
    create_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"))
    answers = db.relationship("Answer", backref="question", lazy="dynamic", cascade='all')

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        import random
        import forgery_py
        random.seed()
        user_count = User.query.count()
        course_count = Courses.query.count()
        for i in range(count):
            user_id = User.query.offset(random.randint(0, user_count - 1)).first().id
            course_id = Courses.query.offset(random.randint(0, course_count - 1)).first().id
            cq = CourseQuestion(question_content=forgery_py.lorem_ipsum.sentence(),
                                create_time=forgery_py.date.date(),
                                author_id=user_id,
                                course_id=course_id)
            db.session.add(cq)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def __repr__(self):
        return '<CourseQuestion %r>' % self.content

    def to_json(self):
        json_question = {
            'id': self.id,
            "question_content": self.question_content,
            "create_time": self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            "author_id": self.author_id,
            "course_id": self.course_id
        }
        return json_question


class Answer(db.Model):
    """
           CourseQuestion: 问大家的回答
           :var id: 主键
           :var content: 回答内容
           :var author_id: 作者id
           :var create_time: 回答时间
           :var question_id:　对应的问题id

           :func to_json
           """
    __table_args__ = {'mysql_charset': 'utf8'}
    __tablename__ = 'answers'
    id = db.Column(db.Integer, primary_key=True)
    answer_content = db.Column(db.String(200))
    create_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    question_id = db.Column(db.Integer, db.ForeignKey("coursequestions.id"))

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        import random
        import forgery_py
        random.seed()
        user_count = User.query.count()
        cq_count = CourseQuestion.query.count()
        for i in range(count):
            user_id = User.query.offset(random.randint(0, user_count - 1)).first().id
            question_id = CourseQuestion.query.offset(random.randint(0, cq_count - 1)).first().id
            answer = Answer(answer_content=forgery_py.lorem_ipsum.sentence(),
                            create_time=forgery_py.date.date(),
                            author_id=user_id,
                            question_id=question_id)
            db.session.add(answer)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def __repr__(self):
        return '<Answer %r>' % self.content

    def to_json(self):
        json_answer = {
            'id': self.id,
            "answer_content": self.answer_content,
            "create_time": self.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            "author_id": self.author_id,
            "question_id": self.question_id
        }
        return json_answer


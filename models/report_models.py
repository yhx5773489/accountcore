# -*- coding: utf-8 -*-
from odoo import models, fields, api
from .main_models import Glob_tag_Model
import uuid


# jexcel表格模型的字段
class Jexcel_fields(models.AbstractModel):
    '''全局标签模型,用于多重继承方式添加到模型'''
    _name = "accountcore.jexcel_fields"
    _description = 'jexcel模型字段'
    data = fields.Text(string='数据内容', default='[[]]')
    data_style = fields.Text(string='模板样式')
    width_info = fields.Text(string='列宽的定义')
    height_info = fields.Text(string='行高的定义')
    header_info = fields.Text(string='表头定义')
    comments_info = fields.Text(string='批注定义')
    merge_info = fields.Text(string='合并单元格定义', default='{}')
    meta_info = fields.Text(string='隐藏的信息定义')


# 报表接收者
class Receiver(models.Model, Glob_tag_Model):
    '''报表接收者'''
    _name = "accountcore.receiver"
    _description = '报表的报送对象'
    number = fields.Char(string='接收者编号')
    name = fields.Char(string='接收者', required=True)
    _sql_constraints = [('accountcore_receiver_name_unique', 'unique(name)',
                         '接收者名称重复了!')]


# 报表类型
class ReportType(models.Model, Glob_tag_Model):
    '''报表类型'''
    _name = 'accountcore.report_type'
    _description = '报表的类型，例如：资产负债表，利润表等'
    number = fields.Char(string='报表类型编号')
    name = fields.Char(string='报表类型名称', required=True)
    _sql_constraints = [('accountcore_reportytpe_name_unique', 'unique(name)',
                         '报表类型名称重复了!')]


# 归档报表
class StorageReport(models.Model, Glob_tag_Model, Jexcel_fields):
    '''归档的报表'''
    _name = 'accountcore.storage_report'
    _description = '归档的报表'
    report_type = fields.Many2one('accountcore.report_type', string='报表类型')
    number = fields.Char(string='归档报表编号')
    name = fields.Char(string='归档报表名称', required=True)
    create_user = fields.Many2one('res.users',
                                  string='归档人',
                                  default=lambda s: s.env.uid,
                                  readonly=True,
                                  required=True,
                                  ondelete='restrict',
                                  index=True)
    start_date = fields.Date(string='数据开始月份')
    end_date = fields.Date(string='数据结束月份')
    orgs = fields.Many2many('accountcore.org', string='机构范围', required=True)
    receivers = fields.Many2many('accountcore.receiver', string='接收者')
    summary = fields.Text(string='归档报表说明')
    # data = fields.Text(string='数据内容', default='[[]]')
    # data_style = fields.Text(string='模板样式')
    # width_info = fields.Text(string='列宽的定义')
    # height_info = fields.Text(string='行高的定义')
    htmlstr = fields.Html(string='html内容')


# 报表模板
class ReportModel(models.Model, Glob_tag_Model, Jexcel_fields):

    '''报表模板'''
    _name = 'accountcore.report_model'
    _description = '报表模板，用于生成报表'
    report_type = fields.Many2one('accountcore.report_type', string='报表类型')
    guid = fields.Char(string='模板唯一码', readonly=True)
    name = fields.Char(string='报表模板名称', required=True)
    version = fields.Char(string='报表模板版本', required=True)
    summary = fields.Text(string='报表模板简介')
    explain = fields.Html(string='报表模板详细介绍')
    # data = fields.Text(string='模板数据', default='[[]]')
    # data_style = fields.Text(string='模板样式')
    # width_info = fields.Text(string='列宽的定义')
    # height_info = fields.Text(string='行高的定义')
    _sql_constraints = [('accountcore_repormodel_name_unique', 'unique(name)',
                         '报表模板唯一码重复了!')]

    '''
    设定模板唯一码
    '''
    @api.model
    def create(self, values):
        if 'name':
            values['guid'] = str(uuid.uuid4())
        return super(ReportModel, self).create(values)



    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=0):
        args = args or []
        # 源代码默认为160,突破其限制   详细见 /web/static/src/js/views/form_common.js
        if limit == 160:
            limit = 0
        pos = self.search(args, limit=limit, order='name')
        # return pos.name_get()
        return pos._my_name_get()

    @api.model
    @api.multi
    def _my_name_get(self):
        result = []
        name = self._rec_name
        if name in self._fields:
            convert = self._fields[name].convert_to_display_name
            for record in self:
                result.append((record.id, convert(
                    record[name], record)+"[版本："+record.version+"]唯一码："+record.guid))
        else:
            for record in self:
                result.append((record.id, "%s,%s" % (
                    record._name, record.guid)))
        return result

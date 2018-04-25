from django.core.files.storage import FileSystemStorage
from fdfs_client.client import Fdfs_client


class FdfsStorage(FileSystemStorage):
    """自定义存储类"""

    def _save(self, name, content):
        """
        当管理员再后台上传文件时,会使用此类保存上传的文件
        :param name: 文件名
        :param content: ImageFieldFile对象 从 此对象 获取上传的文件内容
        :return:
        """
        # path = super()._save(name, content)
        # print(name, path, )

        # todo:保存文件到FastDfs服务器上
        client = Fdfs_client('utils/fdfs/client.conf')
        try:
            # 上传文件到Fdfs服务器
            datas = content.read()  # 要上传的文件内容
            result = client.upload_by_buffer(datas)

            status = result.get('Status')
            if status == "Upload successed.":
                # 成功
                path = result.get('Remote file_id')
            else:
                raise Exception('上传图片失败: %s' % status)

        except Exception as e:
            # 上传文件出错
            print(e)
            raise e

        # 上传的文件路径,此路径需要保存到数据表中
        # print(path)
        return path

    def url(self, name):
        """重写url方法"""
        # 拼接nginx服务器的ip+端口,再返回给浏览器显示
        path = super().url(name)
        return 'http://127.0.0.1:8888/'+path








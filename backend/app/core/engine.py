# app/core/engine.py
from typing import List, Dict

class DocumentProcessorEngine:
    """
    封装文档处理的核心算法，如AAAI论文中的逻辑。
    """

    def collect_hierarchical_nodes(
        self,
        # 注意：这里的输入稍微调整以适应我们的场景
        course_name: str, 
        doc_id: str,
        structured_doc: Dict 
    ) -> List[Dict]:
        """
        将单个结构化文档解析为扁平化的节点列表。
        原函数中的 question 和 question_list 在我们场景下可以理解为 course_name。
        """
        all_nodes = []
        
        # 从 structured_doc 中提取内容
        if "abstract" in structured_doc and structured_doc.get("abstract"):
            for chunk in structured_doc["abstract"]:
                node = {
                    "course_name": course_name,
                    "doc_id": doc_id,
                    "type": "paragraph",
                    "parent_title": "abstract",
                    "parent_type": "abstract",
                    "content": chunk,
                }
                all_nodes.append(node)

        if "sections" in structured_doc:
            for section_title, section_dict in list(structured_doc.get("sections", {}).items()):
                if section_dict.get("content"):
                    for chunk in section_dict["content"]:
                        node = {
                            "course_name": course_name,
                            "doc_id": doc_id,
                            "type": "paragraph",
                            "parent_title": section_title,
                            "parent_type": "section",
                            "content": chunk,
                        }
                        all_nodes.append(node)

                if section_dict.get("subsections"):
                    for subsection_title, subsection_content_list in list(section_dict.get("subsections", {}).items()):
                        if subsection_content_list:
                            for chunk in subsection_content_list:
                                node = {
                                    "course_name": course_name,
                                    "doc_id": doc_id,
                                    "type": "paragraph",
                                    "parent_title": subsection_title,
                                    "parent_type": "subsection",
                                    "grandparent_title": section_title,
                                    "content": chunk,
                                }
                                all_nodes.append(node)
        return all_nodes

// Ví dụ trong Vue.js (sử dụng Axios)
            async downloadDocument(loanProfileId, templateId) {
                try {
                    const response = await axios.post(
                        `/api/loan-profiles/${loanProfileId}/generate-document/`,
                        { template_id: templateId },
                        {
                            responseType: 'blob', // Quan trọng: nhận phản hồi dưới dạng blob
                            headers: {
                                Authorization: `Bearer ${localStorage.getItem('access_token')}` // Nếu dùng JWT
                            }
                        }
                    );

                    const url = window.URL.createObjectURL(new Blob([response.data]));
                    const link = document.createElement('a');
                    link.href = url;
                    // Lấy tên file từ header Content-Disposition
                    const contentDisposition = response.headers['content-disposition'];
                    let filename = 'document.docx';
                    if (contentDisposition) {
                        const filenameMatch = contentDisposition.match(/filename="(.+)"/);
                        if (filenameMatch && filenameMatch.length > 1) {
                            filename = filenameMatch[1];
                        }
                    }
                    link.setAttribute('download', filename);
                    document.body.appendChild(link);
                    link.click();
                    link.remove();
                    window.URL.revokeObjectURL(url);
                    alert('Đã tải xuống tài liệu thành công!');
                } catch (error) {
                    console.error('Lỗi khi tải tài liệu:', error.response || error);
                    alert('Có lỗi xảy ra khi tải tài liệu.');
                }
            }// Ví dụ trong Vue.js (sử dụng Axios)
            async downloadDocument(loanProfileId, templateId) {
                try {
                    const response = await axios.post(
                        `/api/loan-profiles/${loanProfileId}/generate-document/`,
                        { template_id: templateId },
                        {
                            responseType: 'blob', // Quan trọng: nhận phản hồi dưới dạng blob
                            headers: {
                                Authorization: `Bearer ${localStorage.getItem('access_token')}` // Nếu dùng JWT
                            }
                        }
                    );

                    const url = window.URL.createObjectURL(new Blob([response.data]));
                    const link = document.createElement('a');
                    link.href = url;
                    // Lấy tên file từ header Content-Disposition
                    const contentDisposition = response.headers['content-disposition'];
                    let filename = 'document.docx';
                    if (contentDisposition) {
                        const filenameMatch = contentDisposition.match(/filename="(.+)"/);
                        if (filenameMatch && filenameMatch.length > 1) {
                            filename = filenameMatch[1];
                        }
                    }
                    link.setAttribute('download', filename);
                    document.body.appendChild(link);
                    link.click();
                    link.remove();
                    window.URL.revokeObjectURL(url);
                    alert('Đã tải xuống tài liệu thành công!');
                } catch (error) {
                    console.error('Lỗi khi tải tài liệu:', error.response || error);
                    alert('Có lỗi xảy ra khi tải tài liệu.');
                }
            }
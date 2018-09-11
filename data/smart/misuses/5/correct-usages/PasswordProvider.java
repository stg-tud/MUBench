package com.smart.sso.server.provider;

import java.math.BigInteger;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

import com.smart.mvc.exception.ServiceException;
import com.smart.mvc.util.StringUtils;

public class PasswordProvider {

	private static final String SUFFIX = "`1qazx";

	public static String encrypt(String password) {
		if (StringUtils.isBlank(password)) {
			throw new ServiceException("密码不能为空");
		}
		try {
			return md5(new StringBuilder(password).append(SUFFIX).toString());
		}
		catch (Exception e) {
			throw new ServiceException("密码加密错误");
		}
	}

	private static String md5(String str) {
		String password = null;
		try {
			//previously using MD5 which is insecure so changing that to SHA-256
			MessageDigest md = MessageDigest.getInstance("SHA-256");
			
			md.update(str.getBytes());
			password = new BigInteger(1, md.digest()).toString(16);
		}
		catch (NoSuchAlgorithmException e) {
			e.printStackTrace();
		}
		return password;
	}

	public static void main(String[] args) {
		System.err.println("加密        后:" + encrypt("123456"));
	}
}